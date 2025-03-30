import json
from multiprocessing import Pool
from pathlib import Path

from ..benchmark import AbstractBenchmark
from .benchmark import instantiate_benchmark
from .config_file import read_config_file
from .options import Options
from .parser import StatsParser
from .parser.flatjs import FlatJS


def parse_subdir(args: tuple[Path, Path, AbstractBenchmark, StatsParser]) -> dict:
    stats_dir, output_dir, benchmark, parser = args

    bench_name = benchmark.get_name()

    bench_id = stats_dir.name

    output_file = output_dir.joinpath(f"{bench_id}")

    config_file = stats_dir.joinpath(f"config.yaml")
    outlog_file = stats_dir.joinpath(f"output.log")
    stdout_file = stats_dir.joinpath(f"system.terminal")
    stats_file = stats_dir.joinpath(f"stats.txt")

    # Read benchmark configuration
    config = read_config_file(config_file)
    parsed_output = dict(
        output_log=benchmark.parse_output_log(outlog_file),
        stdout_log=benchmark.parse_stdout_log(stdout_file),
    )

    stats_params = dict(
        bench_name=bench_name,
        bench_id=bench_id,
        **benchmark.parse_config(config),
    )
    if output_file.with_suffix(".0.json").exists():
        print(f"parse_subdir: Skipped parsing {bench_id} to {output_file}")
        return stats_params

    print(f"parse_subdir: Parsing {bench_id} to {output_file}")

    parsed_rois = parser.parse_stats(stats_params, parsed_output, stats_file)

    for roi_id, rows in enumerate(parsed_rois):
        fname = f"{output_file}.{roi_id}.json"
        with open(fname, "w") as f:
            json.dump(rows, f)
            f.write("\n")

    return stats_params


def parse_workload(opts: Options) -> int:
    """_summary_

    Args:
        opts (Options): _description_

    Returns:
        int: _description_
    """
    # Instantiate benchmark

    module_path = opts.parse[0]
    benchmark = instantiate_benchmark(module_path, name=module_path.parent.stem)

    # Get benchmark name
    name = benchmark.get_name()

    # Set benchmark configurations directory
    # {workspace_dir}/{name}/{config_output}
    config_output = opts.workspace_dir.joinpath(name, opts.config_output)
    parser_output = opts.workspace_dir.joinpath(name, opts.parser_output)

    # Create benchmark results directory
    parser_output.mkdir(parents=True, exist_ok=True)

    print(f"Parsing results for benchmark {name}")

    stats_dirs = [
        f
        for f in config_output.iterdir()
        if f.is_dir()
        and f.joinpath("stats.txt").is_file()
        and f.joinpath("stats.txt").stat().st_size > 0
    ]

    parser = FlatJS(parser_re_dir=opts.user_data_dir.joinpath("parser"))

    args_list = [
        (stats_dir, parser_output, benchmark, parser) for stats_dir in stats_dirs
    ]
    p_results = []

    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(parse_subdir, args_list)):
            p_results.append(result)

    # for p in args_list[:1]:
    #    parse_subdir(p)

    # Write index
    print(f"Writing index")
    index_file = parser_output.joinpath("index.json")
    with index_file.open("w") as f:
        json.dump(p_results, f)
        f.write("\n")

    return 0
