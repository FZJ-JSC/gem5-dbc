from multiprocessing import Pool
from pathlib import Path

from .options import Options
from .benchmark import instantiate_benchmark
from .config_file import read_config_file, write_config_file

from ..benchmark import AbstractBenchmark
from ..config import Config, check_config
from ..util import add_row_id_col, csv_dict

def write_work_script(opts: Options, config: Config, benchmark: AbstractBenchmark) -> Path:
    """
    Write work script
    """
    benchmark_env = benchmark.get_env(config)
    benchmark_cmd = benchmark.get_command(config)

    output_dir = Path(config.simulation.output_dir)
    work_template = opts.templates_dir.joinpath(config.simulation.work_script).read_text()
    work_script = output_dir.joinpath(config.simulation.work_script)

    work_script.write_text(
        work_template.format(
            benchmark_env="\n".join([f"export {k}=\"{v}\"" for k,v in benchmark_env.items()]),
            benchmark_cmd=benchmark_cmd,
        )
    )

    return work_script


def write_srun_script(opts: Options, config: Config, config_file: Path) -> Path:
    """
    Write srun script
    """
    output_dir = Path(config.simulation.output_dir)
    srun_template = opts.templates_dir.joinpath(config.simulation.launch_script).read_text()
    srun_script = output_dir.joinpath(config.simulation.launch_script)
    srun_script.write_text(
        srun_template.format(
            gem5_bin=opts.gem5_bin,
            gem5_script=opts.gem5_script,
            gem5_script_opts=opts.gem5_script_opts,
            gem5_debug_opts=opts.gem5_debug_opts,
            benchmark_output=output_dir,
            benchmark_config=str(config_file),
        )
    )
    srun_script.chmod(0o744)

    return srun_script


def generate_work_directory(args: tuple[dict,AbstractBenchmark,Options]) -> int:
    """
    Generate work directory for given benchmark parameters
    """
    params, benchmark, opts = args

    # Read config file
    config = read_config_file(opts)
    config.simulation.output_dir = str(opts.results_dir.joinpath(params['row_id']))
    config.parameters = dict([(k,v) for k,v in params.items() if k != "row_id"])

    config = benchmark.get_config(config, config.parameters)

    # Check if config is valid
    if check_config(config) is not True:
        return -1

    # Create output directory
    output_dir = Path(config.simulation.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write config params to local config file
    config_file = output_dir.joinpath("config.yaml")
    config_file = write_config_file(config_file, config)

    write_work_script(opts, config, benchmark)

    write_srun_script(opts, config, config_file)

    return 0


def generate_workload(opts: Options) -> int:
    """
    Generate Workload

    Args:
        opts (Options): _description_

    Raises:
        ValueError: _description_

    Returns:
        int: _description_
    """
    # Instantiate benchmark
    benchmark = instantiate_benchmark(opts.benchmark_mod)

    # Get benchmark name
    name = benchmark.get_name()

    # Set benchmark results directory
    opts.results_dir = opts.results_dir.joinpath(name)

    # Create benchmark results directory
    opts.results_dir.mkdir(parents=True, exist_ok=True)

    print(f"Generate work directories for benchmark {name}")

    if opts.benchmark_cfg is None:
        raise ValueError("Config Path not given")
    
    # Read default benchmark configuration
    config = read_config_file(opts)

    # Generate benchmark parameter list
    parameters = add_row_id_col(benchmark.get_parameter_list(config))

    # Write parameter index
    csv_dict.write(opts.results_dir.joinpath("index.csv"), parameters)

    print(f"Generating {len(parameters)} scripts for {name}")

    args_list = [(p, benchmark, opts) for p in parameters ]
    p_results = []
    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(generate_work_directory, args_list)):
            p_results.append(result)

    #for p in dir_params:
    #    dir_result.append(generate_work_directory(p))

    return 0
