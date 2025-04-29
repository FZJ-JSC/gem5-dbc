import argparse
from dataclasses import dataclass
from pathlib import Path

from ..util import files
from .resources import artifact_db


@dataclass
class Options:
    resource_add: str
    resource_delete: str
    resource_type: str
    resource_version: str
    resource_metadata: str
    resource_arch: str
    generate: str
    init_config: str
    parse: str
    evaluate: str
    validate: bool
    benchmark_dir: Path
    user_conf_dir: Path
    user_data_dir: Path
    artifacts_dir: Path
    workspace_dir: Path
    config_dir: Path
    generated_dir: str
    parsed_dir: str
    parser_format: str
    nprocs: int
    command: str
    artifacts: dict
    file_args: list[Path]

    @classmethod
    def parse_from_args(cls, user_conf_dir: str, user_data_dir: str):
        conf_dir = Path(user_conf_dir)
        data_dir = Path(user_data_dir)
        work_dir = Path.cwd()

        parser = argparse.ArgumentParser(description="Configuration")

        parser.add_argument(
            "--resource-add",
            type=str,
            default="",
            help="Add path object to simulation resource index",
            metavar="path",
        )
        parser.add_argument(
            "--resource-delete",
            type=str,
            default="",
            help="Remove path object from resource index",
            metavar="path",
        )
        parser.add_argument(
            "--resource-type",
            type=str,
            default="",
            help="Simulation resource version",
        )
        parser.add_argument(
            "--resource-version",
            type=str,
            default="",
            help="Simulation resource version",
        )
        parser.add_argument(
            "--resource-metadata",
            type=str,
            default="",
            help="Simulation resource metadata",
        )
        parser.add_argument(
            "--resource-arch",
            type=str,
            default="",
            help="Corresponding architecture of simulation resource to be added",
        )
        parser.add_argument(
            "--generate",
            type=str,
            default="",
            help="Generate simulation scripts for benchmark",
            metavar="benchmark",
        )
        parser.add_argument(
            "--init-config",
            type=str,
            default="",
            help="Initial configuration for benchmark generation",
            metavar="configuration.yaml",
        )
        parser.add_argument(
            "--parse",
            type=str,
            default="",
            help="Parse simulation results in directory",
            metavar="benchmark_dir",
        )
        parser.add_argument(
            "--evaluate",
            type=str,
            default="",
            help="Evaluate parsed simulation statistics after parsing directory",
            metavar="benchmark_dir",
        )
        parser.add_argument(
            "--validate",
            action="store_true",
            help="Validate configuration file",
        )
        parser.add_argument(
            "--benchmark-dir",
            type=str,
            default=None,
            help="Directory to search for benchmark Python modules",
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
            "--config-dir",
            type=str,
            default=None,
            help="Directory to search for architecture configuration files",
        )
        parser.add_argument(
            "--generated-dir",
            type=str,
            default="work",
            help="Generated configuration output directory",
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
        file_args: list[Path] = []
        if args.resource_add:
            if args.resource_type == "":
                raise SystemExit(f"Please specify artifact resource type.")
            command = "resource_add"
            file_args.append(Path(args.resource_add))
        elif args.resource_delete:
            command = "resource_del"
            file_args.append(Path(args.resource_del))
        elif args.generate:
            if args.init_config == "":
                raise SystemExit(
                    f"Please specify initial configuration file or directory."
                )
            command = "generate"
            if (
                _path := files.find(
                    args.generate,
                    work_dir,
                    args.workspace_dir,
                    args.benchmark_dir,
                    args.user_data_dir.joinpath("benchmarks"),
                    main="main",
                    ext="py",
                )
            ) is None:
                raise SystemExit(f"Could not find module {args.generate}.")
            file_args.append(_path)
            if (
                _path := files.find(
                    args.init_config,
                    work_dir,
                    args.workspace_dir,
                    args.config_dir,
                    args.user_data_dir.joinpath("configs"),
                    main="index",
                    ext="yaml",
                )
            ) is None:
                raise SystemExit(
                    f"Could not find configuration file or directory {args.init_config}."
                )
            file_args.append(_path)
            artifacts = artifact_db.read(artifacts_index)
        elif args.parse:
            command = "parse"
            if (
                _path := files.find(
                    args.parse,
                    work_dir,
                    main="main",
                    ext="py",
                )
            ) is None:
                raise SystemExit(f"Could not find module {args.parse}.")
            file_args.append(_path)
        elif args.evaluate:
            command = "evaluate"
            if (
                _path := files.find(
                    args.evaluate,
                    work_dir,
                    main="main",
                    ext="py",
                )
            ) is None:
                raise SystemExit(f"Could not find module {args.evaluate}.")
            file_args.append(_path)
        elif args.validate:
            if args.init_config == "":
                raise SystemExit(
                    f"Please specify initial configuration file or directory."
                )
            command = "validate"
            if (
                _path := files.find(
                    args.init_config,
                    work_dir,
                    args.workspace_dir,
                    args.config_dir,
                    args.user_data_dir.joinpath("configs"),
                    main="index",
                    ext="yaml",
                )
            ) is None:
                raise SystemExit(f"Could not find configuration {args.init_config}.")
            file_args.append(_path)

        opts = cls(
            command=command,
            artifacts=artifacts,
            file_args=file_args,
            **vars(args),
        )

        return opts
