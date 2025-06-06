# YAML Loader with `!include` constructor taken from
# https://gist.github.com/joshbode/569627ced3076931b02f?permalink_comment_id=2309157#gistcomment-2309157

from pathlib import Path

import yaml


class ExtLoaderMeta(type):
    def __new__(metacls, __name__, __bases__, __dict__):
        """Add include constructer to class."""
        # register the include constructor on the class
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        cls.add_constructor("!include", cls.construct_include)
        return cls


class ExtLoader(yaml.Loader, metaclass=ExtLoaderMeta):
    """YAML Loader with `!include` constructor."""

    def __init__(self, stream):
        """Initialise Loader."""
        try:
            self._root = Path(stream.name).resolve().parent
        except AttributeError:
            self._root = Path.cwd()  # path.curdir
        super().__init__(stream)

    def construct_include(self, node):
        """Include file referenced at node."""
        filename = self._root.joinpath(self.construct_scalar(node))
        with filename.open("r") as f:
            if filename.suffix in (".yaml", ".yml"):
                return yaml.load(f, ExtLoader)
            else:
                return "".join(f.readlines())


def read(file: Path) -> dict:
    """
    Read YAML file to Python dict
    Support file import using `!include` tag


    Args:
        file (Path): YAML file path

    Returns:
        dict: YAML file contents as Python dict
    """
    with file.open("r", encoding="UTF-8") as stream:
        data = yaml.load(stream, Loader=ExtLoader)
    return data or dict()


def write(file: Path, data: dict) -> dict:
    """Write Python dict to YAML file

    Args:
        file (Path): YAML file path
        data (dict): Python dict

    Returns:
        dict: Python dict
    """
    data = data or dict()
    with file.open("w", encoding="UTF-8", newline="") as stream:
        yaml.safe_dump(
            data, stream, sort_keys=False, default_flow_style=False, width=1024
        )
    return data
