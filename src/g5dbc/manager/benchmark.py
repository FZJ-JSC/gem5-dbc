import importlib.util
import sys
from pathlib import Path

from ..benchmark import AbstractBenchmark


def instantiate_benchmark(path: Path, name: str | None = None) -> AbstractBenchmark:
    if name is None:
        name = path.stem

    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)

    app = importlib.import_module(name)
    benchmark: AbstractBenchmark = getattr(app, name)()

    return benchmark
