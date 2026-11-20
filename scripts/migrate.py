"""Preview by default. Run again with --apply; interrupted runs are resumable."""
import argparse
import json
import re
from pathlib import Path
from common import atomic, digest, locked, safe
from memory import blocks

SKILL = Path(__file__).resolve().parents[1]
ASSETS = SKILL / "assets/templates"
OLD, NEW = ".opencode", ".project-memory"
LEGACY = SKILL / "references/legacy-v2"


def same_text(a, b):
    return a.replace(b"\r\n", b"\n") == b.replace(b"\r\n", b"\n")


def upgrade(root, apply=False, checkpoint=lambda: None):
    root = root.resolve(strict=True)
    if root == SKILL:
        raise ValueError("Choose the target project, not the Skill repository")
    with locked(root):
        old, new = safe(root, OLD), safe(root, NEW)
        if old.exists() and new.exists():
            raise ValueError("both memory directories exist; reconcile contents before retry")
        base = old if old.exists() else new
        actions = []
        edits = {}
        def current(rel):
            # Before rename, resolve new-path destinations against the old tree.
            key = Path(rel)
            if key.parts[0] == NEW:
                key = Path(base.name, *key.parts[1:])
            p = safe(root, key)
            return p.read_bytes() if p.exists() else None
        def put(rel, data):
            rel = Path(rel)
            if current(rel) != data:
                edits[rel] = data
        if old.exists():
            actions.append(f"rename {OLD} -> {NEW}")
        for name in ("opencode.json", "commands/save.md"):
            rel = Path(NEW, name)
            data = current(rel)
            if data is None:
                continue
            template = (LEGACY / Path(name).name).read_bytes()
            identical = same_text(data, template)
            if name.endswith(".json"):
                try:
                    identical = json.loads(data) == json.loads(template)
                except ValueError:
                    pass
            if not identical:
                raise ValueError(f"custom {name}: retain/export its settings or rules before migration")
            put(rel, None)
        # Rewrite path references only in memory documents and project guidance.
        docs = [root / n for n in ("AGENTS.md", "CONTEXT.md", "LESSONS.md", "README.md")]
        docs += list(base.rglob("*.md")) if base.exists() else []
        docs += list((root / "docs").rglob("*.md")) if (root / "docs").is_dir() else []
        migrating = old.exists() or (new.exists() and not (new / "installed-tools.json").exists())
        for p in docs if migrating else []:
            if not p.exists():
                continue
            safe(root, p.relative_to(root))
            rel = Path(NEW) / p.relative_to(base) if p.is_relative_to(base) else p.relative_to(root)
            if rel in edits:
                continue
            data = p.read_bytes()
            if rel == Path(NEW, "tasks/index.md"):
                legacy_intro = next(line for line in (LEGACY / "tasks/index.md").read_bytes().splitlines()
                                    if line.startswith(b">"))
                if legacy_intro in data:
                    data = data.replace(legacy_intro, "通过任务索引定位，按项目记忆规则恢复上下文。".encode())
                    put(rel, data)
            if OLD.encode() in data:
                def rewrite(chunk):
                    return chunk.replace(OLD.encode() + b"/", NEW.encode() + b"/").replace(
                        OLD.encode() + b"\\", NEW.encode() + b"\\")
                # Keep already marked evidence verbatim even if a quote mentions an old path.
                pieces, offset = [], 0
                for block in blocks(data).values():
                    pieces.extend((rewrite(data[offset:block.start()]), block[0]))
                    offset = block.end()
                put(rel, b"".join(pieces) + rewrite(data[offset:]))
        for name in ("CONTEXT.md", "LESSONS.md", "memory.md", "tasks/index.md",
                     "tasks/templates/context.md", "tasks/templates/progress.md"):
            rel = Path(name) if name in ("CONTEXT.md", "LESSONS.md") else Path(NEW, name)
            original = current(rel)
            stock = LEGACY / name
            if original is None or (stock.is_file() and same_text(original, stock.read_bytes())):
                put(rel, (ASSETS / name).read_bytes())
        ignore = Path(NEW, ".gitignore")
        previous = current(ignore) or b""
        missing = [v for v in (b"/cache/", b"/tools/__pycache__/") if v not in previous.splitlines()]
        if missing:
            put(ignore, previous + (b"\n" if previous and not previous.endswith(b"\n") else b"")
                + b"\n".join(missing) + b"\n")
        rel = Path("AGENTS.md")
        raw = current(rel) or b""
        rules = (ASSETS / rel).read_bytes()
        if not raw or same_text(raw, (LEGACY / rel).read_bytes()):
            put(rel, rules)
        elif b"<!-- project-memory:v3 -->" not in raw and not any(
            marker in raw for marker in (b"SYSTEM CONSTRAINTS", b"TASK MEMORY PROTOCOL", OLD.encode())):
            put(rel, raw + (b"\n" if raw.endswith(b"\n") else b"\n\n") + rules)
        elif b"<!-- project-memory:v3 -->" not in raw:
            # Remove only byte-equivalent legacy paragraphs. Keep human changes.
            legacy = (LEGACY / rel).read_text(encoding="utf-8").strip()
            chunks = re.split(r"\n[ \t]*\n", legacy)
            body = raw.decode("utf-8-sig").replace("\r\n", "\n")
            known = set(chunks)
            body = "\n\n".join(c for c in re.split(r"\n[ \t]*\n", body.strip()) if c not in known)
            body = body.replace(OLD + "/", NEW + "/").replace(OLD + "\\", NEW + "\\")
            if re.search(r"(?i)opencode|/save", body):
                raise ValueError("custom AGENTS.md contains legacy host rules; review before switching")
            put(rel, (body.rstrip() + "\n\n").encode() + rules)
        # Install uniquely owned helpers. Never replace locally customized copies.
        owned = {p.name: p for p in (SKILL / "scripts").glob("*.py") if p.name != "migrate.py"}
        owned = {Path(NEW, "tools", n): p for n, p in owned.items()}
        for dest, src in (("semantics.md", "memory-semantics.md"), ("operations.md", "operations.md"),
                          ("code-map.md", "code-map.md")):
            owned[Path(NEW, dest)] = SKILL / "references" / src
        manifest = Path(NEW, "installed-tools.json")
        previous_manifest = current(manifest)
        installed = json.loads(previous_manifest) if previous_manifest else {}
        checksums = {}
        for rel, src in owned.items():
            data = src.read_bytes()
            existing = current(rel)
            name = rel.as_posix()
            checksums[name] = digest(data)
            if existing is not None and existing != data and digest(existing) != installed.get(name):
                raise ValueError(f"local tool/reference differs: {rel}; review before replacing")
            put(rel, data)
        put(manifest, (json.dumps(checksums, indent=2, sort_keys=True)+"\n").encode())
        for rel, data in edits.items():
            actions.append(("remove " if data is None else "write ") + rel.as_posix())
        if apply:
            if old.exists():
                old.rename(new)
                checkpoint()
            for rel, data in edits.items():
                dest = safe(root, rel)
                if data is None:
                    dest.unlink()
                else:
                    atomic(dest, data)
                checkpoint()
        return actions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        print("\n".join(upgrade(args.project, args.apply)) or "up to date")
    except (OSError, ValueError) as error:
        parser.exit(1, str(error) + "\n")
