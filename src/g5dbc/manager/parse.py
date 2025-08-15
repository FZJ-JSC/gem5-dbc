from multiprocessing import Pool
from pathlib import Path

from ..benchmark import AbstractBenchmark
from ..stats.flatjs import FlatJS
from ..util import dict_csv, dict_json
from .benchmark import load_benchmark
from .config_file import read_config_file
from .options import Options


def find_glob(path: Path, glob: str) -> Path | None:
    l = sorted(p for p in path.glob(glob) if p.is_file() and p.stat().st_size > 0)
    return l[0] if l else None


def parse_results(args: tuple[Options, AbstractBenchmark, Path]) -> dict:
    """Parse simulation results directory

    Args:
        args (tuple[Options, AbstractBenchmark, Path]): Command line options, benchmark instance, results directory path

    Returns:
        dict: Set of simulation parameters for current simulation
    """

    opts, bm, stats_dir = args

    bench_id = stats_dir.name

    output_file = Path(opts.output_dir).joinpath(opts.parsed_dir, bench_id)

    parser = FlatJS(parser_re_dir=Path(opts.parser_regex_dir))

    # Read benchmark configuration
    config = read_config_file(stats_dir.joinpath(f"config.yaml"))
    parsed_output = dict(
        output_log=bm.parse_output_log(stats_dir.joinpath(f"output.log")),
        stdout_log=bm.parse_stdout_log(stats_dir.joinpath(f"system.terminal")),
    )

    stats_params: dict[str, str | int | float] = dict(
        bench_name=bm.name,
        bench_id=bench_id,
        **bm.get_column_keys(config),
    )

    print(f"parse_results: Parsing {bench_id} to {output_file}")

    stat_name = find_glob(stats_dir, "stats.txt*")
    parsed_rois = (
        parser.parse_stats(
            stats_params,
            parsed_output,
            stat_name,
        )
        if stat_name is not None
        else dict()
    )

    for roi_id, roi_cols in parsed_rois.items():
        dict_json.write(Path(f"{output_file}.{roi_id}.json"), roi_cols)

    stats_params["n_roi"] = len(parsed_rois)

    return stats_params


def parse_workload(opts: Options):
    """Parse benchmark results

    Args:
        opts (Options): Command line options
    """

    # Instantiate benchmark
    bm: AbstractBenchmark = load_benchmark(Path(opts.parse))

    # Set benchmark work and parsed directory
    workld_dir = Path(opts.output_dir).joinpath(opts.workld_dir)
    parsed_dir = Path(opts.output_dir).joinpath(opts.parsed_dir)

    # Create benchmark results directory
    parsed_dir.mkdir(parents=True, exist_ok=True)

    # Check if index.csv already created
    index_file = parsed_dir.joinpath("index.csv")
    parsed_stats = dict_csv.read(index_file)
    parsed_ids: set[str] = set([f["bench_id"] for f in parsed_stats])

    print(f"Parsing results for benchmark {bm.name}")

    stats_dirs = [
        workld_dir.joinpath(d)
        for d in set(
            [
                f.name
                for f in workld_dir.iterdir()
                if f.name not in parsed_ids and find_glob(f, "stats.txt*") is not None
            ]
        )
    ]

    args_list = [(opts, bm, stats_dir) for stats_dir in stats_dirs]

    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(parse_results, args_list)):
            parsed_stats.append(result)

    # for p in args_list[:1]:
    #    parse_results(p)

    # Write index
    print(f"Writing index")
    dict_csv.write(index_file, sorted(parsed_stats, key=lambda x: x["bench_id"]))
