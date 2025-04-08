import hashlib
from pathlib import Path


def find(name: str, *paths: Path, main="main", ext="py") -> Path | None:
    """Search for a file or subdirectory in a list of paths.

    Args:
        name (str): File or subdirectory name to search.
        *paths: (Path): List of paths to search.
        main (str, optional): Default file name. Defaults to "main".
        ext (str, optional): Default file suffix. Defaults to "py".

    Returns:
        Path | None: Returns a Path object pointing to file if found, otherwise None
    """
    search_path = [Path(".")]
    search_path.extend(paths)
    for p in search_path:
        fname = p.joinpath(name)
        if not fname.suffix:
            if fname.is_dir():
                fname = Path(p).joinpath(name, f"{main}.{ext}")
            else:
                fname = Path(p).joinpath(f"{name}.{ext}")
        if fname.exists():
            return fname.resolve()
    return None


def hash_md5(path: Path, update_bytes=4096) -> str:
    """Returh MD5 hash of file

    Args:
        path (Path): Path to file
        update_bytes (int, optional): Hash update size in bytes. Defaults to 4096.

    Returns:
        str: Hash value as a string of hexadecimal digits
    """
    hash = hashlib.md5()
    with path.open("rb") as f:
        for data in iter(lambda: f.read(update_bytes), b""):
            hash.update(data)
    return hash.hexdigest()


def write_template(output_dir: Path, template: Path, **kwargs) -> Path:
    """Write a template file

    Args:
        output_dir (Path): Output directory
        template (Path): Path to file template
        **kwargs: Template parameters

    Returns:
        Path: Path to output file
    """
    output_file = output_dir.joinpath(template.name)
    if kwargs:
        output_file.write_text(template.read_text().format(**kwargs))
    else:
        output_file.write_bytes(template.read_bytes())
    return output_file
