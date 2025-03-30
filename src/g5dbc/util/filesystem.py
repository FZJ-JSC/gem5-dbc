from pathlib import Path


def find_file(name: str, *paths, main="main", ext="py") -> Path | None:
    search_path = ["."]
    search_path.extend(paths)
    for p in search_path:
        fname = Path(p).joinpath(name)
        if not fname.suffix:
            if fname.is_dir():
                fname = Path(p).joinpath(name, f"{main}.{ext}")
            else:
                fname = Path(p).joinpath(f"{name}.{ext}")
        if fname.exists():
            return fname.resolve()
    return None
