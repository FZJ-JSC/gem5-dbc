import math
from multiprocessing import Pool
from pathlib import Path
from shutil import copy2

from ..benchmark import AbstractBenchmark
from ..config import check_config
from ..util import dict_csv, files
from .benchmark import load_benchmark
from .config_file import read_config_file, write_config_file
from .options import Options
from .resources import read_artifact_index


def generate_bench_id(data: list[dict]) -> list[dict]:
    """Sort parameter list and add bench_id column

    Args:
        data (list[dict]): List of parameter iterations

    Returns:
        list[dict]: Sorted parameter iterations list with additional bench_id column
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


def generate_work_directory(args: tuple[Options, AbstractBenchmark, str, dict]) -> int:
    """Generate work directory for given benchmark parameters

    Args:
        args (tuple[Options, AbstractBenchmark, str, dict]): Command line options, benchmark instance, benchmark ID, params

    Raises:
        FileNotFoundError: Error if gem5 binary could not be found

    Returns:
        int: Returns 0 if successful
    """

    opts, bm, bench_id, params = args

    base_dir = Path(opts.output_dir).joinpath(bm.name)
    workld_dir = base_dir.joinpath(opts.workld_dir, bench_id)

    # Read default benchmark configuration
    config = read_config_file(base_dir.joinpath("index.yaml"), parameters=params)
    config = bm.get_updated_config(config)

    # Check if config is valid
    assert check_config(config), f"Configuration file {bench_id} inconsistent"

    # Get gem5 binary with correct version
    gem5_bin = config.search_artifacts(
        typename="GEM5",
        name=config.simulation.gem5_binary,
        version=config.simulation.gem5_version,
    )

    if not gem5_bin:
        raise FileNotFoundError(
            f"Could not find requested gem5 binary name='{config.simulation.gem5_binary}' version='{config.simulation.gem5_version}'. "
            f"Please add the correct gem5 binary to your artifact index files, {opts.artifact_index}, ",
            f"or update the configured version in your initial system configuration file {opts.init_config}.",
        )

    # Update simulation info
    config.simulation.gem5_binary = gem5_bin[0].name
    config.simulation.gem5_version = gem5_bin[0].version
    config.simulation.output_dir = str(workld_dir)

    # Create output directory
    workld_dir.mkdir(parents=True, exist_ok=True)

    if config.simulation.full_system:
        # Write work script
        files.write_template(
            workld_dir,
            Path(opts.templates_dir).joinpath(config.simulation.work_script),
            benchmark_cmd=bm.get_bench_command(config),
            benchmark_env="\n".join(
                [
                    'export {}="{}"'.format(k, v)
                    for k, v in bm.get_env_vars(config).items()
                ]
            ),
        )
    else:
        config.simulation.se_cmd = bm.get_bench_command(config).split()
        config.simulation.se_env = [
            f"{k}={v}" for k, v in bm.get_env_vars(config).items()
        ]

    # Write srun script
    files.write_template(
        workld_dir,
        Path(opts.templates_dir).joinpath(config.simulation.srun_script),
        gem5_bin=gem5_bin[0].path,
        gem5_script=base_dir.joinpath(config.simulation.gem5_script),
        gem5_workdir=workld_dir,
        gem5_output=config.simulation.output_log,
    ).chmod(0o744)

    # Write config params to local config file
    config_file = workld_dir.joinpath("config.yaml")
    config_file = write_config_file(config_file, config)

    return 0


def generate_workload(opts: Options):
    """Generate workload directories

    Args:
        opts (Options): Command line options

    Raises:
        FileExistsError: Error if benchmark index file already exists
    """

    # Instantiate benchmark
    bm: AbstractBenchmark = load_benchmark(Path(opts.generate))

    # Read default benchmark configuration with artifacts
    config = read_config_file(
        Path(opts.init_config), artifacts=read_artifact_index(opts)
    )

    # Base directory
    base_dir = Path(opts.output_dir).joinpath(bm.name)

    # Set benchmark configurations directory
    workld_dir = base_dir.joinpath(opts.workld_dir)

    # Create benchmark results directory
    workld_dir.mkdir(parents=True, exist_ok=True)

    # Write default configuration to base directory
    write_config_file(base_dir.joinpath("index.yaml"), config)

    # Copy benchmark Python module
    copy2(
        opts.generate,
        base_dir.joinpath("main.py"),
    )

    # Copy wrapper srun.py
    copy2(
        Path(opts.templates_dir).joinpath(config.simulation.gem5_script),
        base_dir.joinpath(config.simulation.gem5_script),
    )

    print(f"Generate work directories for benchmark {bm.name}")

    # Generate benchmark parameter list
    parameters = generate_bench_id(bm.get_parameter_list(config))

    # Write parameter index
    index_file = workld_dir.joinpath("index.csv")
    if index_file.exists():
        raise FileExistsError(f"Benchmark index file {index_file} already exists")
    else:
        dict_csv.write(index_file, parameters)

    print(f"Generating {len(parameters)} scripts for {bm.name}")

    args_list = [(opts, bm, p.pop("bench_id"), p) for p in parameters]
    p_results = []
    with Pool(processes=opts.nprocs) as pool:
        for result in list(pool.imap_unordered(generate_work_directory, args_list)):
            p_results.append(result)

    # for p in dir_params:
    #    dir_result.append(generate_work_directory(p))
