import argparse
from pathlib import Path


def parse_args(data_dir: Path, args=None) -> dict:
    """Parse command line arguments to dict

    Args:
        data_dir (Path): Local user shared data directory
        args (_type_, optional): Command line arguments. Defaults to None.

    Returns:
        dict: Dictionary of command line arguments
    """

    curr_dir = Path.cwd()

    parser = argparse.ArgumentParser(
        description="gem5 simulation framework",
    )
    parser.add_argument(
        "-a",
        "--resource-add",
        type=str,
        default="",
        help="Add path object to simulation resource index",
        metavar="path",
    )
    parser.add_argument(
        "-d",
        "--resource-del",
        type=str,
        default="",
        help="Remove path object from resource index",
        metavar="path",
    )
    parser.add_argument(
        "-T",
        "--resource-type",
        type=str,
        default="",
        help="Simulation resource type",
    )
    parser.add_argument(
        "-N",
        "--resource-name",
        type=str,
        default="",
        help="Simulation resource name",
    )
    parser.add_argument(
        "-M",
        "--resource-meta",
        type=str,
        default="",
        help="Simulation resource metadata",
    )
    parser.add_argument(
        "-A",
        "--resource-arch",
        type=str,
        default="",
        help="Simulation resource architecture.",
    )
    parser.add_argument(
        "-H",
        "--resource-hash",
        type=str,
        default="",
        help="Simulation resource checksum.",
    )
    parser.add_argument(
        "-V",
        "--resource-version",
        type=str,
        default="",
        help="Simulation resource version",
    )
    parser.add_argument(
        "-g",
        "--generate",
        type=str,
        default="",
        help="Generate simulation scripts for benchmark",
        metavar="benchmark.py",
    )
    parser.add_argument(
        "--generate-index-se",
        type=str,
        default="",
        help="Generate artifact index for SE mode simulation",
        metavar="artifact_dir",
    )
    parser.add_argument(
        "-c",
        "--init-config",
        type=str,
        default="",
        help="Initial configuration for benchmark generation",
        metavar="configuration.yaml",
    )
    parser.add_argument(
        "--se-exec",
        type=str,
        default="",
        help="Executable for SE simulation",
        metavar="binary.exe",
    )
    parser.add_argument(
        "--gem5-version",
        type=str,
        default="",
        help="Version of gem5 to use when generating simulation scripts",
    )
    parser.add_argument(
        "--parse",
        type=str,
        default="",
        help="Parse simulation results in directory",
        metavar="benchmark",
    )
    parser.add_argument(
        "--evaluate",
        type=str,
        default="",
        help="Evaluate parsed simulation statistics after parsing directory",
        metavar="benchmark",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate configuration file",
    )
    parser.add_argument(
        "-i",
        "--artifact-index",
        action="append",
        default=[],
        help="Artifacts Directory containing index.yaml",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        default=str(curr_dir),
        help="Output Directory",
    )
    parser.add_argument(
        "--modules-dir",
        type=str,
        default=str(data_dir.joinpath("benchmarks")),
        help="Directory to search for templates",
    )
    parser.add_argument(
        "--configs-dir",
        type=str,
        default=str(data_dir.joinpath("configs")),
        help="Directory to search for templates",
    )
    parser.add_argument(
        "--parser-regex-dir",
        type=str,
        default=str(data_dir.joinpath("parser")),
        help="Directory to search for templates",
    )
    parser.add_argument(
        "--templates-dir",
        type=str,
        default=str(data_dir.joinpath("templates")),
        help="Directory to search for templates",
    )
    parser.add_argument(
        "--workld-dir",
        type=str,
        default="work",
        help="Generated simulation output directory",
    )
    parser.add_argument(
        "--parsed-dir",
        type=str,
        default="parsed",
        help="Parsed results output directory",
    )
    parser.add_argument(
        "--parser-format",
        type=str,
        default="flatjs",
        help="Parser output format",
    )
    parser.add_argument(
        "--compress-stats",
        type=str,
        default="",
        help="Command for stats output compression",
    )
    parser.add_argument(
        "--nprocs",
        type=int,
        default=1,
        help="Number of processes in process pool",
    )

    return vars(parser.parse_args(args=args))
