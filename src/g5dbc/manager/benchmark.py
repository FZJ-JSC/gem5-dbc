import inspect
from pathlib import Path

from ..benchmark import AbstractBenchmark
from ..util import load_mod
from .options import Options


def load_benchmark(opts: Options, path: Path | None) -> AbstractBenchmark:
    """Load AbstractBenchmark implementation from given Python module

    Args:
        opts (Options): Command line options
        path (Path | None): Path to benchmark Python module

    Raises:
        SystemExit: Error if no path given or no Params class found or no AbstractBenchmark implementation found.

    Returns:
        AbstractBenchmark: Instance of AbstractBenchmark implementation defined in given Python module
    """
    if path is None:
        raise SystemExit(f"No path for benchmark Python module given.")

    module_cls = load_mod(path)

    # Load Parameter Class
    _, param_cls = next(
        iter(
            inspect.getmembers(
                module_cls,
                lambda m: inspect.isclass(m) and m.__name__ == "Params",
            )
        ),
        (None, None),
    )

    _, bench_cls = next(
        iter(
            inspect.getmembers(
                module_cls,
                lambda m: inspect.isclass(m)
                and ("AbstractBenchmark" in [y.__name__ for y in m.__mro__][1:]),
            )
        ),
        (None, None),
    )

    if param_cls is None:
        raise SystemExit(f"No Params class found in Python module.")

    if bench_cls is None:
        raise SystemExit(f"No Benchmark class found in Python module.")

    b: AbstractBenchmark = bench_cls(param_cls=param_cls)

    return b
