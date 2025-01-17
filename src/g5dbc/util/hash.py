import hashlib
from pathlib import Path

def md5sum(path: Path, update_bytes = 4096) -> str:
    hash = hashlib.md5()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(update_bytes), b""):
            hash.update(data)
    return hash.hexdigest()
