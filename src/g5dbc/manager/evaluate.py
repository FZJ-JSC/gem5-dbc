from multiprocessing import Pool
from pathlib import Path

from ..benchmark import AbstractBenchmark
from ..util import dict_csv, dict_json
from .benchmark import load_benchmark
from .options import Options


def evaluate_file(args: tuple[AbstractBenchmark, Path]) -> list[dict]:
    benchmark, stats_file = args
    return benchmark.get_data_rows_from_stats(dict_json.read(stats_file))


def evaluate_results(opts: Options, path_mod: Path):
    """Evaluate parsed results

    Args:
        opts (Options): Command line options
        path_mod (Path): Path to benchmark Python module
    """

    # Instantiate benchmark
    bm: AbstractBenchmark = load_benchmark(opts, path_mod)

    # Get benchmark name
    name = bm.name

    parsed_dir = opts.workspace_dir.joinpath(name, opts.parsed_dir)

    # Check if index.csv already created
    parsed_stats = dict_csv.read(parsed_dir.joinpath("index.csv"))

    print(f"Evaluating results for benchmark {name}")

    parsed_files = filter(
        lambda x: x.is_file(),
        [
            parsed_dir.joinpath(f"{p['bench_id']}.{n}.json")
            for p in parsed_stats
            for n in range(int(p["n_roi"]))
        ],
    )

    args_list = [(bm, f) for f in parsed_files]

    data_rows = []
    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(evaluate_file, args_list)):
            data_rows.extend(result)

    dict_csv.write(
        parsed_dir.joinpath("data.csv"),
        sorted(data_rows, key=lambda x: (x["bench_name"], x["bench_id"], x["roi_id"])),
    )
