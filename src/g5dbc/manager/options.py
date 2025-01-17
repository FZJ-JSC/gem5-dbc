import argparse
from dataclasses import dataclass
from pathlib import Path

from ..util.filesystem import find_file


@dataclass
class Options:
    configure: list[str]
    generate: list[Path]
    parse: list[Path]
    user_conf_dir: Path
    user_data_dir: Path
    artifacts_dir: Path
    workspace_dir: Path
    config_output: str
    parser_output: str
    parser_format: str
    nprocs: int
    command: str

    @classmethod
    def parse_from_args(cls, user_conf_dir: str, user_data_dir: str):
        conf_dir = Path(user_conf_dir)
        data_dir = Path(user_data_dir)
        work_dir = Path.cwd()

        parser = argparse.ArgumentParser(description="Configuration")

        parser.add_argument(
            "--configure",
            type=str,
            default=None,
            nargs=2,
            help="Configure default values",
            metavar=("type", "value"),
        )
        parser.add_argument(
            "--generate",
            type=str,
            default=None,
            nargs=2,
            help="Generate simulation scripts",
            metavar=("benchmark", "configuration"),
        )
        parser.add_argument(
            "--parse",
            type=str,
            default=None,
            nargs=1,
            help="Parse simulation results",
            metavar="benchmark_dir",
        )
        parser.add_argument(
            "--user-conf-dir",
            type=str,
            default=None,
            help="User Configuration Directory",
        )
        parser.add_argument(
            "--user-data-dir",
            type=str,
            default=None,
            help="User Data Directory containing templates and parser subdirectories",
        )
        parser.add_argument(
            "--artifacts-dir",
            type=str,
            default=None,
            help="Artifacts Directory",
        )
        parser.add_argument(
            "--workspace-dir",
            type=str,
            default=None,
            help="Workspace Directory",
        )
        parser.add_argument(
            "--config-output",
            type=str,
            default="config",
            help="Generated configuration output directory",
        )
        parser.add_argument(
            "--parser-output",
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
            "--nprocs",
            type=int,
            default=1,
            help="Number of processes in process pool",
        )

        args = parser.parse_args()

        args.user_conf_dir = (
            conf_dir if args.user_conf_dir is None else Path(args.user_conf_dir)
        )
        args.user_data_dir = (
            data_dir if args.user_data_dir is None else Path(args.user_data_dir)
        )
        args.artifacts_dir = (
            data_dir if args.artifacts_dir is None else Path(args.artifacts_dir)
        )
        args.workspace_dir = (
            work_dir if args.workspace_dir is None else Path(args.workspace_dir)
        )

        command = ""
        if args.configure:
            command = "configure"
        elif args.generate:
            command = "generate"
            args.generate[0] = find_file(
                args.generate[0],
                ".py",
                work_dir,
                args.workspace_dir,
                data_dir.joinpath("benchmarks"),
                args.user_data_dir.joinpath("benchmarks"),
            )
            args.generate[1] = find_file(
                args.generate[1],
                ".yaml",
                work_dir,
                args.workspace_dir,
                data_dir.joinpath("configs"),
                args.user_data_dir.joinpath("configs"),
            )
        elif args.parse:
            command = "parse"
            args.parse[0] = find_file(
                args.parse[0], ".py", work_dir.joinpath(args.parse[0])
            )

        return cls(command=command, **vars(args))
