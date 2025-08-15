import bz2
import gzip
import hashlib
import lzma
from contextlib import contextmanager
from pathlib import Path
from typing import Generator, TextIO


def find(name: str, *search_path: str, main="main", ext="py") -> Path | None:
    """Search for a file or subdirectory in a list of paths.

    Args:
        name (str): File or subdirectory name to search.
        *search_path: (str): List of paths to search.
        main (str, optional): Default file name. Defaults to "main".
        ext (str, optional): Default file suffix. Defaults to "py".

    Returns:
        Path | None: Returns a Path object pointing to file if found, otherwise None
    """
    if name != "":
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


@contextmanager
def open_file(path: Path, mode="rt", encoding="utf-8") -> Generator[TextIO, None, None]:
    """Open stats file according to file extension

    Args:
        path (Path): File Path
        mode (str, optional): Read mode. Defaults to "rt".
        encoding (str, optional): Encoding. Defaults to "utf-8".

    Yields:
        Generator[TextIO]: File Object
    """
    fh: TextIO
    s = str(path)
    if s.endswith((".xz", ".lzma")):
        fh = lzma.open(path, mode, encoding=encoding)
    elif s.endswith(".gz"):
        fh = gzip.open(path, mode, encoding=encoding)
    elif s.endswith(".bz2"):
        fh = bz2.open(path, mode, encoding=encoding)
    else:
        fh = path.open(mode, encoding=encoding)

    try:
        yield fh
    finally:
        fh.close()
