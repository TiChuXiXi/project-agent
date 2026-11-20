"""Register source you actually read, with its observed hash and map block token."""
import argparse
from pathlib import Path
from common import safe, digest
from memory import save

MAP = ".project-memory/code-map/entries.md"


def register(root, source, fingerprint, token, note):
    path = safe(root, source)
    if not path.is_file() or digest(path.read_bytes()) != fingerprint:
        raise ValueError("source changed or missing; re-read before mapping")
    rel = path.relative_to(root).as_posix()
    key = "code-" + digest(rel.encode())[:24]
    return save(root, MAP, key, token, f"source: {rel}\nsha256: {fingerprint}\n{note}")


def freshness(root, body):
    lines = body.splitlines()
    if len(lines)<2 or not lines[0].startswith("source: ") or not lines[1].startswith("sha256: "):
        return "unknown"
    path = safe(root, lines[0][8:])
    if not path.is_file():
        return "missing"
    return "current" if digest(path.read_bytes()) == lines[1][8:] else "stale"


if __name__ == "__main__":
    import json
    from memory import read
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("source")
    p.add_argument("--sha", help="observed SHA256")
    p.add_argument("--token", help="observed map block token")
    p.add_argument("--note", type=Path, help="UTF-8 file describing responsibility, aliases, symbols, related files and constraints")
    a = p.parse_args()
    r = Path.cwd().resolve()
    try:
        src = safe(r,a.source)
        if a.note:
            print(register(r,a.source,a.sha,a.token,a.note.read_text(encoding="utf-8")))
        else:
            key = "code-" + digest(src.relative_to(r).as_posix().encode())[:24]
            print(json.dumps(dict(sha=digest(src.read_bytes()), **read(r,MAP,key)),ensure_ascii=False))
    except (OSError,ValueError) as error:
        p.exit(1,str(error)+"\n")
