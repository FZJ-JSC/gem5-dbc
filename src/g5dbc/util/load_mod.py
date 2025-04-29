import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def load_mod(path: Path, name: str = "") -> ModuleType:
    """Import a Python module from a given file

    Args:
        path (Path): Path of the module file
        name (str, optional): Module name. If not given defaults to path stem.

    Raises:
        SystemExit: If Python module could not be loaded

    Returns:
        ModuleType: Loaded Python Module
    """
    if not name:
        name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"No Python module found.")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)

    mod = importlib.import_module(name)

    return mod
