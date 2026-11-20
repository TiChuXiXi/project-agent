"""Local derived SQLite FTS5 index. REF identifies a specific passage and its bytes."""
import argparse
import base64
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from common import digest, locked, safe
from memory import blocks, documents, GOAL
from code_map import freshness

CACHE = ".project-memory/cache/search-v1.sqlite"


def terms(text):
    parts = re.findall(r"[\u3400-\u9fff]+|[^\W\u3400-\u9fff]+", unicodedata.normalize("NFKC", text).lower())
    words = []
    for p in parts:
        if "\u3400" <= p[0] <= "\u9fff":
            words.extend(p[i:i+2] for i in range(len(p)-1)) if len(p)>1 else words.append(p)
        else:
            words.append(p)
    return list(dict.fromkeys(words))


def sources(root):
    by_path = {p: set() for p in documents(root) if not (
        p.parent == root/".project-memory" and p.name in {"semantics.md","operations.md","code-map.md"})}
    if (root/"README.md").is_file():
        by_path[safe(root,"README.md")] = set()
    cfg = safe(root,".project-memory/sources.txt")
    for line in cfg.read_text(encoding="utf-8").splitlines() if cfg.exists() else []:
        rel, _, heading = line.strip().partition("#")
        if not rel:
            continue
        path = safe(root,rel)
        if path.suffix.lower() != ".md":
            raise ValueError("expected Markdown source: "+rel)
        if path.is_file() and not (path in by_path and not by_path[path]):
            by_path.setdefault(path,set()).add(heading)
    return by_path


def passages(data, allowed):
    lines = data.decode("utf-8-sig").splitlines(keepends=True)
    bmap = {}
    for key,m in blocks(data).items():
        start = data[:m.start()].count(b"\n")
        bmap[start] = (key,m[0].count(b"\n") or 1,m[2].decode())
    stack = []
    i = 0
    while i<len(lines):
        line = lines[i].rstrip()
        heading = re.match(r"^(#{1,6})\s+(.+)",line)
        if heading:
            level = len(heading[1])
            stack = [(l,t) for l,t in stack if l<level] + [(level,heading[2])]
        visible = not allowed or "" in allowed or any(t in allowed for _,t in stack)
        title = " / ".join(t for _,t in stack)
        if i in bmap:
            key,size,body = bmap[i]
            if visible:
                yield i+1,key,title,body
            i += size
        elif not visible or not line or heading:
            i += 1
        else:
            start = i
            i += 1
            while (not line.startswith("|") and i<len(lines) and i not in bmap and
                   lines[i].strip() and not lines[i].startswith(("#","|"))):
                i += 1
            yield start+1,"",title,"".join(lines[start:i])


def reference(rel,line,body):
    return base64.urlsafe_b64encode(json.dumps([rel,line,digest(body.encode())],ensure_ascii=False).encode()).decode()


def snapshot(root, path, allowed):
    data = path.read_bytes()
    rel = path.relative_to(root).as_posix()
    for line,key,title,body in passages(data,allowed):
        yield (rel,line,key,title,body,reference(rel,line,body)," ".join(terms(" ".join([rel,key,title,body]))))


def index(root,rebuild=False):
    dbpath = safe(root,CACHE)
    dbpath.parent.mkdir(parents=True,exist_ok=True)
    db = sqlite3.connect(dbpath)
    try:
        if rebuild:
            db.executescript("DROP TABLE IF EXISTS docs; DROP TABLE IF EXISTS ft;")
        db.execute("CREATE TABLE IF NOT EXISTS docs(path TEXT PRIMARY KEY, hash TEXT)")
        db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS ft USING fts5(path UNINDEXED,line UNINDEXED,key UNINDEXED,title UNINDEXED,body UNINDEXED,ref UNINDEXED,terms)")
        prior = dict(db.execute("SELECT path,hash FROM docs"))
        with db:
            for path,allowed in sources(root).items():
                rel = path.relative_to(root).as_posix()
                data = path.read_bytes()
                stamp = digest(data + json.dumps(sorted(allowed)).encode())
                if prior.pop(rel,None) == stamp:
                    continue
                db.execute("DELETE FROM ft WHERE path=?",(rel,))
                rows = ((rel,n,k,t,b,reference(rel,n,b)," ".join(terms(" ".join([rel,k,t,b]))))
                        for n,k,t,b in passages(data,allowed))
                db.executemany("INSERT INTO ft VALUES(?,?,?,?,?,?,?)",rows)
                db.execute("INSERT OR REPLACE INTO docs VALUES(?,?)",(rel,stamp))
            for rel in prior:
                db.execute("DELETE FROM ft WHERE path=?",(rel,))
                db.execute("DELETE FROM docs WHERE path=?",(rel,))
        return db
    except BaseException:
        db.close()
        raise


def alternatives(root, query):
    """Expand only explicitly maintained exact aliases, retaining multiword queries."""
    path = safe(root, "CONTEXT.md")
    result = [terms(query)]
    if path.is_file():
        section = blocks(path.read_bytes()).get("aliases")
        for line in section[2].decode().splitlines() if section else []:
            names, separator, evidence = line.partition(" | ")
            group = [part.strip() for part in names.split("=") if part.strip()]
            if separator and evidence.strip() and query.casefold().strip() in [s.casefold() for s in group]:
                result.extend(terms(s) for s in group)
    return [group for group in result if group]


def search(root,query,history=False,limit=12,kind=None):
    tokens = terms(query)
    if not tokens:
        return []
    with locked(root):
        groups = alternatives(root,query)
        try:
            db = index(root)
        except (sqlite3.DatabaseError,PermissionError):
            # Raw Markdown is authoritative even with an unavailable/corrupt cache.
            rows = [row for path, allowed in sources(root).items() for row in snapshot(root,path,allowed)]
            keys = [row[2] for row in rows]
            rows = [r[:6] for r in rows if any(all(t in r[6].split() for t in group) for group in groups)]
        else:
            try:
                keys = [r[0] for r in db.execute("SELECT key FROM ft WHERE key GLOB 'G-*'")]
                match = " OR ".join("(" + " AND ".join('"'+t+'"' for t in group) + ")" for group in groups)
                rows = db.execute("SELECT path,line,key,title,body,ref FROM ft WHERE ft MATCH ? ORDER BY rank",(match,)).fetchall()
            finally:
                db.close()
        latest = {}
        for key in keys:
            g = GOAL.fullmatch(key)
            if g:
                latest[g[1]] = max(latest.get(g[1],0),int(g[2]))
        hits = []
        for rel,n,key,title,body,ref in rows:
            g = GOAL.fullmatch(key)
            historic = bool((g and int(g[2]) < latest[g[1]]) or re.search(r"(?im)^\s*(?:状态|status)\s*[:：]\s*superseded\b",body))
            if historic and not history:
                continue
            category = ("code" if key.startswith("code-") else "lesson" if rel=="LESSONS.md" else
                        "task" if "/tasks/" in rel else "context" if rel=="CONTEXT.md" else "project")
            if kind and category != kind:
                continue
            status = re.search(r"(?im)^\s*(?:状态|status)\s*[:：]\s*(active|candidate|superseded)\b",body)
            evidence = re.findall(r"\b(user_confirmed|source_verified|agent_proposed)\b",body)
            hits.append(dict(path=rel,line=n,id=key,title=title,kind=category,ref=ref,
                evidence=list(dict.fromkeys(evidence)),
                state=freshness(root,body) if category=="code" else "historical" if historic else status[1] if status else "recorded",
                snippet=body[:360]))
        if not history:
            hits.sort(key=lambda h: h["state"] in {"stale","missing","candidate"})
        return hits[:limit]


def get(root,ref):
    rel,line,_ = json.loads(base64.urlsafe_b64decode(ref))
    path = safe(root,rel)
    allowed = sources(root)
    if path in allowed:
        for r in snapshot(root,path,allowed[path]):
            if r[1]==line and r[5]==ref:
                return r[4]
    raise ValueError("source changed, missing or excluded; repeat search")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd",required=True)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--history",action="store_true")
    s.add_argument("--kind",choices=["code","lesson","task","context","project"])
    sub.add_parser("get").add_argument("ref")
    sub.add_parser("rebuild")
    a = p.parse_args()
    root = Path.cwd().resolve()
    try:
        if a.cmd=="search":
            print(json.dumps(search(root,a.query,a.history,kind=a.kind),ensure_ascii=False,indent=2))
        elif a.cmd=="get":
            print(get(root,a.ref))
        else:
            with locked(root):
                safe(root,CACHE).unlink(missing_ok=True)
                index(root).close()
            print("rebuilt")
    except (OSError,ValueError,sqlite3.DatabaseError) as error:
        p.exit(1,str(error)+"\n")
