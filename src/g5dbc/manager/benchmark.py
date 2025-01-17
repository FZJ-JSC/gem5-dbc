import importlib.util
import sys
from pathlib import Path

from ..benchmark import AbstractBenchmark


def instantiate_benchmark(path: Path) -> AbstractBenchmark:
    benchmark_name = path.stem

    spec = importlib.util.spec_from_file_location(benchmark_name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module.__name__] = module
    spec.loader.exec_module(module)

    app = importlib.import_module(benchmark_name)
    benchmark: AbstractBenchmark = getattr(app, benchmark_name)()

    return benchmark
