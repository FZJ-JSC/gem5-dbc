import math
from multiprocessing import Pool
from pathlib import Path
from shutil import copy2

from ..benchmark import AbstractBenchmark
from ..config import check_config
from ..util import dict_csv, files, load_cls
from .config_file import read_config_file, write_config_file
from .options import Options


def generate_bench_id(data: list[dict]) -> list[dict]:
    """
    Sort parameter list and add bench_id column
    """
    # sort dictionaries
    cols = [str(k) for k in data[0].keys()]
    rows = sorted([tuple(p[col] for col in cols) for p in data])
    npad = math.ceil(math.log10(len(rows)))
    cols.append("bench_id")
    idx_data = [
        dict(list(zip(cols, row)))
        for row in [(*r, str(r_id).zfill(npad)) for r_id, r in enumerate(rows)]
    ]

    return idx_data


def generate_work_directory(args: tuple[AbstractBenchmark, str, dict]) -> int:
    """
    Generate work directory for given benchmark parameters
    """
    benchmark, bench_id, params = args

    base_dir = benchmark.workspace_dir.joinpath(benchmark.name)
    output_dir = benchmark.generated_dir.joinpath(bench_id)

    # Read default benchmark configuration
    config = read_config_file(base_dir.joinpath("index.yaml"), parameters=params)
    config = benchmark.get_updated_config(config)

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
            f"Please check your local artifact index."
        )

    # Update simulation info
    config.simulation.gem5_binary = gem5_bin.name
    config.simulation.gem5_version = gem5_bin.version
    config.simulation.output_dir = str(output_dir)

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write config params to local config file
    config_file = output_dir.joinpath("config.yaml")
    config_file = write_config_file(config_file, config)

    # Write work script
    files.write_template(
        output_dir,
        benchmark.user_data_dir.joinpath("templates", config.simulation.work_script),
        benchmark_cmd=benchmark.get_bench_command(config),
        benchmark_env="\n".join(
            [
                'export {}="{}"'.format(k, v)
                for k, v in benchmark.get_env_vars(config).items()
            ]
        ),
    )

    # Write srun script
    files.write_template(
        output_dir,
        benchmark.user_data_dir.joinpath("templates", config.simulation.srun_script),
        gem5_bin=gem5_bin.path,
        gem5_script=base_dir.joinpath(config.simulation.gem5_script),
        gem5_workdir=output_dir,
        gem5_output=config.simulation.output_log,
    ).chmod(0o744)

    return 0


def generate_workload(opts: Options, path_mod: Path, path_cfg: Path):
    """Generate Workload

    Args:
        opts (Options): Command line options
        path_mod (Path): Benchmark module
        path_cfg (Path): Default configuration

    Raises:
        FileExistsError: Error if benchmark index file already exists
    """
    # Instantiate benchmark
    benchmark: AbstractBenchmark = load_cls(
        path_mod,
        workspace_dir=opts.workspace_dir,
        user_data_dir=opts.user_data_dir,
        generated_dir=opts.generated_dir,
    )

    # Read default benchmark configuration with artifacts
    config = read_config_file(path_cfg, artifacts=opts.artifacts)

    # Base directory
    base_dir = opts.workspace_dir.joinpath(benchmark.name)

    # Set benchmark configurations directory
    # {workspace_dir}/{name}/{generated_dir}
    generated_dir = base_dir.joinpath(opts.generated_dir)

    # Create benchmark results directory
    generated_dir.mkdir(parents=True, exist_ok=True)

    # Write default configuration to base directory
    write_config_file(base_dir.joinpath("index.yaml"), config)

    # Copy benchmark Python module
    copy2(
        path_mod,
        base_dir.joinpath("main.py"),
    )

    # Copy wrapper srun.py
    copy2(
        opts.user_data_dir.joinpath("templates", config.simulation.gem5_script),
        base_dir.joinpath(config.simulation.gem5_script),
    )

    print(f"Generate work directories for benchmark {benchmark.name}")

    # Generate benchmark parameter list
    parameters = generate_bench_id(benchmark.get_parameter_list(config))

    # Write parameter index
    index_file = generated_dir.joinpath("index.csv")
    if index_file.exists():
        raise FileExistsError(f"Benchmark index file {index_file} already exists")
    else:
        dict_csv.write(index_file, parameters)

    print(f"Generating {len(parameters)} scripts for {benchmark.name}")

    args_list = [(benchmark, p.pop("bench_id"), p) for p in parameters]
    p_results = []
    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(generate_work_directory, args_list)):
            p_results.append(result)

    # for p in dir_params:
    #    dir_result.append(generate_work_directory(p))
