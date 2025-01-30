from pathlib import Path


def find_file(name: str, suffix: str, *paths) -> Path | None:
    fname = Path(name)
    if not fname.suffix:
        fname = Path(f"{name}{suffix}")
    if fname.exists():
        return fname.resolve()
    for p in paths:
        if Path(p).joinpath(fname).exists():
            return Path(p).joinpath(fname).resolve()
    return None
