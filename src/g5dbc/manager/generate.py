from multiprocessing import Pool
from pathlib import Path
from shutil import copy2

from ..benchmark import AbstractBenchmark
from ..config import check_config
from ..util import add_row_id_col, csv_dict
from .benchmark import instantiate_benchmark
from .config_file import read_config_file, write_config_file
from .options import Options


def write_template(output_dir: Path, template: Path, **kwargs) -> Path:
    output_file = output_dir.joinpath(template.name)
    if kwargs:
        output_file.write_text(template.read_text().format(**kwargs))
    else:
        output_file.write_bytes(template.read_bytes())
    return output_file


def generate_work_directory(args: tuple[dict, AbstractBenchmark, Options]) -> int:
    """
    Generate work directory for given benchmark parameters
    """
    params, benchmark, opts = args

    benchmark_cfg = opts.generate[1]

    # Read config file
    config = read_config_file(benchmark_cfg, opts.artifacts)

    name = benchmark.get_name()
    configs_dir = opts.workspace_dir.joinpath(name, opts.config_output)

    config.simulation.output_dir = str(configs_dir.joinpath(params["row_id"]))
    config.parameters = dict([(k, v) for k, v in params.items() if k != "row_id"])

    config = benchmark.update_config(config.parameters, config)

    # Check if config is valid
    if not check_config(config):
        return -1

    # Get gem5 binary with correct version
    gem5_bin = config.get_artifact(
        typename="GEM5",
        name=config.simulation.gem5_binary,
        version=config.simulation.gem5_version,
    )

    if gem5_bin is None:
        raise Exception(
            f"Could not find gem5 binary '{config.simulation.gem5_binary}' version '{config.simulation.gem5_version}'. "
            f"Please check your local artifact index {opts.user_conf_dir}."
        )

    # Update simulation info
    config.simulation.gem5_binary = gem5_bin.name
    config.simulation.gem5_version = gem5_bin.version

    # Create output directory
    output_dir = Path(config.simulation.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write config params to local config file
    config_file = output_dir.joinpath("config.yaml")
    config_file = write_config_file(config_file, config)

    # Write work script
    write_template(
        output_dir,
        opts.user_data_dir.joinpath("templates", config.simulation.work_script),
        benchmark_cmd=benchmark.get_command(config),
        benchmark_env="\n".join(
            [
                'export {}="{}"'.format(k, v)
                for k, v in benchmark.get_env(config).items()
            ]
        ),
    )

    # Write srun script
    write_template(
        output_dir,
        opts.user_data_dir.joinpath("templates", config.simulation.srun_script),
        gem5_bin=gem5_bin.path,
        gem5_script=configs_dir.parent.joinpath(config.simulation.gem5_script),
        gem5_workdir=output_dir,
        gem5_output=config.simulation.output_log,
    ).chmod(0o744)

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
    benchmark_mod = opts.generate[0]
    benchmark_cfg = opts.generate[1]

    if benchmark_mod is None:
        raise SystemExit(f"No benchmark found.")

    benchmark = instantiate_benchmark(benchmark_mod)

    # Get benchmark name
    name = benchmark.get_name()

    # Set benchmark configurations directory
    # {workspace_dir}/{name}/{config_output}
    configs_dir = opts.workspace_dir.joinpath(name, opts.config_output)

    # Create benchmark results directory
    configs_dir.mkdir(parents=True, exist_ok=True)

    # Read default benchmark configuration
    config = read_config_file(benchmark_cfg)

    # Copy benchmark python module
    src = benchmark_mod
    dst = configs_dir.parent.joinpath("main.py")
    copy2(src, dst)

    # Copy wrapper srun.py
    src = opts.user_data_dir.joinpath("templates", config.simulation.gem5_script)
    dst = configs_dir.parent.joinpath(config.simulation.gem5_script)
    copy2(src, dst)

    print(f"Generate work directories for benchmark {name}")

    # Generate benchmark parameter list
    parameters = add_row_id_col(benchmark.get_parameter_list(config))

    # Write parameter index
    index_file = configs_dir.joinpath("index.csv")
    if index_file.exists():
        raise FileExistsError(f"Index file {index_file} already exists")
    else:
        csv_dict.write(index_file, parameters)

    print(f"Generating {len(parameters)} scripts for {name}")

    args_list = [(p, benchmark, opts) for p in parameters]
    p_results = []
    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(generate_work_directory, args_list)):
            p_results.append(result)

    # for p in dir_params:
    #    dir_result.append(generate_work_directory(p))

    return 0
