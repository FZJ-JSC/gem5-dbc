from multiprocessing import Pool
from pathlib import Path

from ..benchmark import AbstractBenchmark
from ..util import dict_csv, dict_json, load_cls
from .config_file import read_config_file
from .options import Options
from .parser import StatsParser
from .parser.flatjs import FlatJS


def parse_subdir(args: tuple[AbstractBenchmark, Path]) -> dict:
    benchmark, stats_dir = args

    name = benchmark.name

    bench_id = stats_dir.name

    output_file = benchmark.workspace_dir.joinpath(
        name, benchmark.parsed_dir, f"{bench_id}"
    )

    parser = FlatJS(parser_re_dir=benchmark.user_data_dir.joinpath("parser"))

    config_file = stats_dir.joinpath(f"config.yaml")

    # Read benchmark configuration
    config = read_config_file(config_file)
    parsed_output = dict(
        output_log=benchmark.parse_output_log(stats_dir.joinpath(f"output.log")),
        stdout_log=benchmark.parse_stdout_log(stats_dir.joinpath(f"system.terminal")),
    )

    stats_params: dict[str, str | int | float] = dict(
        bench_name=name,
        bench_id=bench_id,
        **benchmark.get_column_keys(config),
    )

    print(f"parse_subdir: Parsing {bench_id} to {output_file}")

    parsed_rois = parser.parse_stats(
        stats_params, parsed_output, stats_dir.joinpath(f"stats.txt")
    )

    for roi_id, roi_cols in parsed_rois.items():
        dict_json.write(Path(f"{output_file}.{roi_id}.json"), roi_cols)

    stats_params["n_roi"] = len(parsed_rois)

    return stats_params


def parse_workload(opts: Options, path_mod: Path):
    """Parse benchmark results

    Args:
        opts (Options): Command line options
        path_mod (Path): Benchmark directory to parse
    """
    # Instantiate benchmark
    benchmark: AbstractBenchmark = load_cls(
        path_mod,
        name=path_mod.parent.stem,
        workspace_dir=opts.workspace_dir,
        user_data_dir=opts.user_data_dir,
        parsed_dir=opts.parsed_dir,
    )

    # Get benchmark name
    name = benchmark.name

    # Set benchmark configurations directory
    # {workspace_dir}/{name}/{generated_dir}
    generated_dir = opts.workspace_dir.joinpath(name, opts.generated_dir)
    parsed_dir = opts.workspace_dir.joinpath(name, opts.parsed_dir)

    # Create benchmark results directory
    parsed_dir.mkdir(parents=True, exist_ok=True)

    # Check if index.csv already created
    index_file = parsed_dir.joinpath("index.csv")
    parsed_stats = dict_csv.read(index_file)
    parsed_ids: set[str] = set([f["bench_id"] for f in parsed_stats])

    print(f"Parsing results for benchmark {name}")

    stats_dirs = [
        (f.name, f)
        for f in generated_dir.iterdir()
        if f.is_dir()
        and f.joinpath("stats.txt").is_file()
        and f.joinpath("stats.txt").stat().st_size > 0
        and f.name not in parsed_ids
    ]

    args_list = [(benchmark, stats_dir) for _, stats_dir in stats_dirs]

    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(parse_subdir, args_list)):
            parsed_stats.append(result)

    # for p in args_list[:1]:
    #    parse_subdir(p)

    # Write index
    print(f"Writing index")
    dict_csv.write(index_file, sorted(parsed_stats, key=lambda x: x["bench_id"]))
