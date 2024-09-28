from multiprocessing import Pool
from pathlib import Path
import json

from .options import Options
from .benchmark import instantiate_benchmark

from ..benchmark import AbstractBenchmark
from ..config import Config
from ..util import yaml_dict

from ..parser import StatsParser
from ..parser.flatjs import FlatJS


def parse_subdir(args: tuple[Path,Path,AbstractBenchmark,StatsParser]) -> dict:
    stats_dir, output_dir, benchmark, parser = args

    name = stats_dir.name

    output_file = output_dir.joinpath(f"{name}")
    
    config_file = stats_dir.joinpath(f"config.yaml")
    outlog_file = stats_dir.joinpath(f"output.log")
    stdout_file = stats_dir.joinpath(f"system.terminal")
    stats_file  = stats_dir.joinpath(f"stats.txt")

    print(f"parse_subdir: Parsing {stats_dir.name} to {output_file}")

    # Read benchmark configuration
    config = Config.from_dict(yaml_dict.load(config_file))
    parsed_output = dict(
        output_log = benchmark.parse_output_log(outlog_file),
        stdout_log = benchmark.parse_stdout_log(stdout_file)
    )

    stats_params = dict(bench_id=name,**benchmark.parse_config(config))

    parsed_rois = parser.parse_stats(stats_params, parsed_output, stats_file)

    for roi_id,rows in enumerate(parsed_rois):
        fname = f"{output_file}.{roi_id}.json"
        with open(fname, 'w') as f:
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
    benchmark = instantiate_benchmark(opts.benchmark_mod)

    # Get benchmark name
    name = benchmark.get_name()

    # Set benchmark results and parsing directory
    opts.results_dir = opts.results_dir.joinpath(name)
    opts.parser_out  = opts.parser_out.joinpath(name)

    # Create benchmark results directory
    opts.parser_out.mkdir(parents=True, exist_ok=True)

    print(f"Parsing results for benchmark {name}")

    stats_dirs = [f for f in opts.results_dir.iterdir()
                    if f.is_dir()
                    and f.joinpath("stats.txt").is_file()
                    and  f.joinpath("stats.txt").stat().st_size > 0]

    parser = FlatJS(parser_re_dir=opts.parser_re_dir)
    
    args_list = [(stats_dir, opts.parser_out, benchmark, parser) for stats_dir in stats_dirs ]
    p_results = []

    with Pool(processes=opts.nprocs) as pool:
       for result in list(pool.imap_unordered(parse_subdir, args_list)):
           p_results.append(result)

    #for p in args_list[:1]:
    #    parse_subdir(p)

    # Write index
    print(f"Writing index")
    index_file = opts.parser_out.joinpath("index.json")
    with index_file.open('w') as f:
        json.dump(p_results, f)
        f.write("\n")

    return 0