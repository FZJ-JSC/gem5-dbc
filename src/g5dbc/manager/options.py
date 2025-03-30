import argparse
from dataclasses import dataclass, field
from pathlib import Path

from ..util.filesystem import find_file
from .artifact_db import artifact_db_read


@dataclass
class Options:
    resource_add: list[str]
    resource_delete: list[str]
    generate: list[Path]
    parse: list[Path]
    validate: Path
    config_dir: Path
    benchmark_dir: Path
    user_conf_dir: Path
    user_data_dir: Path
    artifacts_dir: Path
    workspace_dir: Path
    config_output: str
    parser_output: str
    parser_format: str
    nprocs: int
    command: str
    artifacts: dict
    resource_version: str | None
    resource_metadata: str | None
    resource_arch: str | None

    @classmethod
    def parse_from_args(cls, user_conf_dir: str, user_data_dir: str):
        conf_dir = Path(user_conf_dir)
        data_dir = Path(user_data_dir)
        work_dir = Path.cwd()

        parser = argparse.ArgumentParser(description="Configuration")

        parser.add_argument(
            "--resource-add",
            type=str,
            default=None,
            nargs=2,
            help="Add path object to simulation resource index",
            metavar=("type", "path"),
        )
        parser.add_argument(
            "--resource-delete",
            type=str,
            default=None,
            nargs=1,
            help="Remove path object from resource index",
            metavar=("path"),
        )
        parser.add_argument(
            "--resource-version",
            type=str,
            default=None,
            help="Simulation resource version",
        )
        parser.add_argument(
            "--resource-metadata",
            type=str,
            default=None,
            help="Simulation resource metadata",
        )
        parser.add_argument(
            "--resource-arch",
            type=str,
            default=None,
            help="Corresponding architecture of simulation resource to be added",
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
            "--validate",
            type=str,
            default=None,
            help="User Configuration to validate",
        )
        parser.add_argument(
            "--user-conf-dir",
            type=str,
            default=None,
            help="User Configuration Directory containing global artifacts.yaml",
        )
        parser.add_argument(
            "--user-data-dir",
            type=str,
            default=None,
            help="User Data Directory containing templates and parser subdirectories",
        )
        parser.add_argument(
            "--config-dir",
            type=str,
            default=None,
            help="Directory to search for architecture configuration files",
        )
        parser.add_argument(
            "--benchmark-dir",
            type=str,
            default=None,
            help="Directory to search for benchmark python modules",
        )
        parser.add_argument(
            "--artifacts-dir",
            type=str,
            default=None,
            help="Artifacts Directory containing index.yaml",
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
        args.workspace_dir = (
            work_dir if args.workspace_dir is None else Path(args.workspace_dir)
        )
        args.config_dir = (
            args.user_data_dir.joinpath("configs")
            if args.config_dir is None
            else Path(args.config_dir)
        )
        args.benchmark_dir = (
            args.user_data_dir.joinpath("benchmarks")
            if args.benchmark_dir is None
            else Path(args.benchmark_dir)
        )
        args.artifacts_dir = (
            args.user_data_dir.joinpath("artifacts")
            if args.artifacts_dir is None
            else Path(args.artifacts_dir)
        )

        artifacts_index = [
            args.user_conf_dir.joinpath("artifacts.yaml"),
            args.artifacts_dir.joinpath("index.yaml"),
        ]

        command = ""
        artifacts = dict()
        if args.resource_add:
            command = "resource_add"
        elif args.resource_delete:
            command = "resource_del"
        elif args.generate:
            command = "generate"
            artifacts = artifact_db_read(artifacts_index)
            args.generate[0] = find_file(
                args.generate[0],
                work_dir,
                args.workspace_dir,
                args.benchmark_dir,
                args.user_data_dir.joinpath("benchmarks"),
                main="main",
                ext="py",
            )
            args.generate[1] = find_file(
                args.generate[1],
                work_dir,
                args.workspace_dir,
                args.config_dir,
                args.user_data_dir.joinpath("configs"),
                main="index",
                ext="yaml",
            )
        elif args.parse:
            command = "parse"
            args.parse[0] = find_file(
                args.parse[0],
                work_dir,
                main="main",
                ext="py",
            )
        elif args.validate:
            command = "validate"
            args.validate = find_file(
                args.validate,
                work_dir,
                args.workspace_dir,
                args.config_dir,
                args.user_data_dir.joinpath("configs"),
                main="index",
                ext="yaml",
            )

        opts = cls(
            command=command,
            artifacts=artifacts,
            **vars(args),
        )

        return opts
