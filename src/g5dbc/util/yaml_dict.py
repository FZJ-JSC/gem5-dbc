# YAML Loader with `!include` constructor taken from 
# https://gist.github.com/joshbode/569627ced3076931b02f?permalink_comment_id=2309157#gistcomment-2309157

import yaml
from pathlib import Path

class ExtLoaderMeta(type):
    def __new__(metacls, __name__, __bases__, __dict__):
        """Add include constructer to class."""
        # register the include constructor on the class
        cls = super().__new__(metacls, __name__, __bases__, __dict__)
        cls.add_constructor('!include', cls.construct_include)
        return cls

class ExtLoader(yaml.Loader, metaclass=ExtLoaderMeta):
    """YAML Loader with `!include` constructor."""
    def __init__(self, stream):
        """Initialise Loader."""
        try:
            self._root = Path(stream.name).resolve().parent
        except AttributeError:
            self._root = Path.cwd() #path.curdir
        super().__init__(stream)
    def construct_include(self, node):
        """Include file referenced at node."""
        filename = self._root.joinpath(self.construct_scalar(node))
        with filename.open('r') as f:
            if filename.suffix in ('.yaml', '.yml'):
                return yaml.load(f, ExtLoader)
            else:
                return ''.join(f.readlines())

def load(file: Path) -> dict:
    with file.open('r') as stream:
        data = yaml.load(stream, Loader=ExtLoader)
    return data

def write(file: Path, data: dict):
    with file.open('w', encoding='utf-8', newline='') as stream:
        yaml.dump(data, stream, default_flow_style=False)
    return data
