"""Shared filesystem primitives for project memory writers (Python 3.9+)."""
import contextlib
import hashlib
import os
from pathlib import Path
import tempfile
import time


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe(root, relative):
    path = root / relative
    if not path.resolve().is_relative_to(root) or path.resolve() != path.absolute():
        raise ValueError(f"outside project or linked path: {relative}")
    return path


@contextlib.contextmanager
def locked(root):
    # OS releases the advisory lock on process death. Every v3 writer uses it.
    name = digest(os.path.normcase(str(root)).encode())
    path = Path(tempfile.gettempdir()) / ("project-memory-" + name + ".lock")
    with path.open("a+b") as file:
        if path.stat().st_size == 0:
            file.write(b"0")
            file.flush()
        file.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(file.fileno(), msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(file, fcntl.LOCK_EX)
        yield


def atomic(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".pm-write-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if path.exists():
            os.chmod(tmp, path.stat().st_mode)
        os.replace(tmp, path)
    finally:
        Path(tmp).unlink(missing_ok=True)
