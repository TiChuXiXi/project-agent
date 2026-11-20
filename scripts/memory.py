"""Compare-and-save Markdown blocks. Read before drafting; pass the observed token."""
import argparse
import json
import re
import uuid
from pathlib import Path
from common import atomic, digest, locked, safe

ID = r"[A-Za-z0-9][A-Za-z0-9_.@-]*"
MARK = re.compile(rb"^<!-- pm:("+ID.encode()+rb") -->\r?\n(.*?)^<!-- /pm -->[ \t]*(?:\r?\n|\Z)", re.M | re.S)
LOGICAL = re.compile(r"(?:G-\d+@v[1-9]\d*|[DP]-\d+)$")
GOAL = re.compile(r"(G-\d+)@v([1-9]\d*)$")


def blocks(data):
    matches = list(MARK.finditer(data))
    if data.count(b"<!-- pm:") != len(matches) or data.count(b"<!-- /pm -->") != len(matches):
        raise ValueError("malformed memory blocks; repair before editing")
    result = {}
    for match in matches:
        key = match[1].decode()
        if key in result or b"<!-- pm:" in match[2]:
            raise ValueError("duplicate or nested block: " + key)
        result[key] = match
    return result


def documents(root):
    for name in ("AGENTS.md", "CONTEXT.md", "LESSONS.md"):
        path = safe(root, name)
        if path.is_file():
            yield path
    base = safe(root, ".project-memory")
    for path in sorted(base.rglob("*.md")):
        parts = path.relative_to(base).parts
        if set(parts[:-1]) & {"conflicts","cache","tools","templates"}:
            continue
        yield safe(root, path.relative_to(root))


def locations(root, key):
    bare = bool(re.fullmatch(r"G-\d+", key))
    found = []
    for path in documents(root):
        for item in blocks(path.read_bytes()):
            if item == key or (bare and item.startswith(key + "@v") and GOAL.fullmatch(item)):
                found.append((item, path.relative_to(root).as_posix()))
    if bare and found:
        version = max(int(i.split("@v")[1]) for i, _ in found)
        found = [(i,p) for i,p in found if i == key + "@v" + str(version)]
    return found


def resolve(root, key):
    found = locations(root, key)
    if len(found) != 1:
        raise ValueError(f"{key}: {'ambiguous' if found else 'missing'} {found}")
    return found[0]


def docpath(root, rel):
    path = safe(root, rel)
    parts = path.relative_to(root).parts
    if path.suffix != ".md" or (parts[0] != ".project-memory" and
        parts not in [("AGENTS.md",), ("CONTEXT.md",), ("LESSONS.md",)]):
        raise ValueError("expected a project memory Markdown document")
    if set(parts[:-1]) & {"conflicts", "tools", "cache", "templates"}:
        raise ValueError("not a writable record")
    return path


def read(root, rel, key):
    path = docpath(root, rel)
    data = path.read_bytes() if path.exists() else b""
    match = blocks(data).get(key)
    return {"token": digest(match[0]) if match else "missing",
            "body": match[2].decode() if match else ""}


def save(root, rel, key, token, body, change_source=None):
    if not re.fullmatch(ID, key) or (re.match(r"^[GDP]-\d", key) and not LOGICAL.fullmatch(key)):
        raise ValueError("invalid ID (goals need @vN)")
    if any(mark in text for mark in ("<!-- pm:", "<!-- /pm -->") for text in (body, change_source or "")):
        raise ValueError("reserved block delimiter in input")
    path = docpath(root, rel)
    with locked(root):
        data = path.read_bytes() if path.exists() else b""
        match = blocks(data).get(key)
        def conflict(reason):
            dest = safe(root, ".project-memory/conflicts/" + uuid.uuid4().hex + ".json")
            atomic(dest, json.dumps(dict(reason=reason, file=str(rel), id=key, observed=token,
                  current=match[2].decode() if match else None, proposed=body,
                  change_source=change_source), ensure_ascii=False, indent=2).encode())
            raise ValueError(f"{reason}; preserved proposal: {dest}")
        goal = GOAL.fullmatch(key)
        if goal and int(goal[2]) > 1 and not (change_source or "").strip():
            conflict("user change source required")
        content = body + ("" if body.endswith("\n") else "\n")
        if change_source:
            content += "\n调整依据：" + change_source + "\n"
        if LOGICAL.fullmatch(key):
            hits = locations(root, key)
            if hits and hits != [(key, path.relative_to(root).as_posix())]:
                conflict("ID moved or already assigned: " + str(hits))
        if match and match[2] == content.encode():
            return "unchanged"
        if token != (digest(match[0]) if match else "missing"):
            conflict("concurrent block change")
        if goal and match:
            conflict("confirmed goal is immutable")
        if goal and not match:
            history = locations(root, goal[1])
            expected = int(history[0][0].split("@v")[1])+1 if len(history)==1 else 1
            if len(history)>1 or int(goal[2]) != expected:
                conflict("invalid goal revision sequence")
        record = f"<!-- pm:{key} -->\n{content}<!-- /pm -->\n".encode()
        if match:
            updated = data[:match.start()] + record + data[match.end():]
        else:
            updated = data + (b"\n" if not data or data.endswith(b"\n") else b"\n\n") + record
        atomic(path, updated)
        return "saved"


def main():
    p = argparse.ArgumentParser(description=__doc__)
    s = p.add_subparsers(dest="cmd", required=True)
    for name in ("read","save"):
        cmd = s.add_parser(name)
        cmd.add_argument("file")
        cmd.add_argument("id")
        if name == "save":
            cmd.add_argument("token")
            cmd.add_argument("input", type=Path)
            cmd.add_argument("--change-source")
    s.add_parser("resolve").add_argument("id")
    args = p.parse_args()
    root = Path.cwd().resolve()
    try:
        if args.cmd == "read":
            out = read(root, args.file, args.id)
        elif args.cmd == "resolve":
            out = resolve(root, args.id)
        else:
            out = save(root,args.file,args.id,args.token,args.input.read_bytes().decode("utf-8"),args.change_source)
        print(json.dumps(out,ensure_ascii=False))
    except (ValueError,OSError) as err:
        p.exit(1, str(err)+"\n")

if __name__ == "__main__":
    main()
