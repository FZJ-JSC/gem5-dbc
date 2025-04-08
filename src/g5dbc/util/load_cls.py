import importlib.util
import sys
from pathlib import Path


def load_cls(path: Path | None, name: str = "", **kwargs):
    """Instantiate class from Python module

    Args:
        path (Path | None): Path of the module
        name (str, optional): Name of the class in module. If empty, defaults to path.stem.

    Raises:
        SystemExit: If Python module could not be loaded

    Returns:
        Any: Instance of class
    """
    if path is None:
        raise SystemExit(f"No Python module found.")
    if name == "":
        name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"No Python module found.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)

    mod = importlib.import_module(name)

    return getattr(mod, name)(**kwargs)
