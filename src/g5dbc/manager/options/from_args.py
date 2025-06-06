from pathlib import Path

from ...util import files
from .options import Options
from .parse_args import parse_args


def from_args(user_conf_dir: str = "", user_data_dir: str = "", args=None) -> Options:
    """Construct Options from command line arguments

    Args:
        user_conf_dir (str, optional): Local user configuration directory. Defaults to "".
        user_data_dir (str, optional): Local user shared data directory. Defaults to "".
        args (_type_, optional): Command line arguments. Defaults to None.

    Raises:
        SystemExit: Exits on error

    Returns:
        Options: Constructed Options instance
    """

    conf_dir = Path(user_conf_dir)
    data_dir = Path(user_data_dir)

    opts = Options(**parse_args(data_dir=data_dir, args=args))

    curr_dir = str(Path.cwd())

    if opts.resource_add:
        opts.command = "resource_add"

        path = Path(opts.resource_add).resolve()
        if not path.exists():
            raise SystemExit(f"Could not find {path}.")
        opts.resource_add = str(path)

        path = conf_dir.joinpath("artifacts.yaml")
        if opts.artifact_index:
            path = files.find(
                opts.artifact_index[0],
                curr_dir,
                main="index",
                ext="yaml",
            )
            if path is None:
                fname = Path(opts.artifact_index[0])
                if fname.suffix == ".yaml" and fname.parent.is_dir():
                    path = fname
                elif not fname.suffix and fname.is_dir():
                    path = fname.joinpath("index.yaml")
                else:
                    raise SystemExit(f"Could not access artifact index {fname}.")
        opts.artifact_index = [str(path)]

        return opts

    if opts.resource_del:
        opts.command = "resource_del"

        path = conf_dir.joinpath("artifacts.yaml")
        if opts.artifact_index:
            path = files.find(
                opts.artifact_index[0],
                curr_dir,
                main="index",
                ext="yaml",
            )
            if path is None:
                raise SystemExit(
                    f"Could not find artifact index {opts.artifact_index[0]}."
                )
        opts.artifact_index = [str(path)]

        return opts

    if opts.generate:
        opts.command = "generate"

        module_path = files.find(
            opts.generate,
            curr_dir,
            opts.modules_dir,
            main="main",
            ext="py",
        )
        if module_path is None:
            raise SystemExit(f"Could not find module {opts.generate}.")
        opts.generate = str(module_path)

        config_path = files.find(
            opts.init_config,
            curr_dir,
            opts.configs_dir,
            main="index",
            ext="yaml",
        )
        if config_path is None:
            raise SystemExit(f"Could not find configuration {opts.init_config}.")
        opts.init_config = str(config_path)

        artifact_index = []
        path = conf_dir.joinpath("artifacts.yaml")
        if path.exists():
            artifact_index.append(str(path))
        for f in opts.artifact_index:
            path = files.find(
                f,
                curr_dir,
                main="index",
                ext="yaml",
            )
            if path is None:
                raise SystemExit(f"Could not find artifact index {f}.")
            artifact_index.append(str(path))

        opts.artifact_index = artifact_index

        opts.output_dir = str(
            Path(opts.output_dir).resolve() if opts.output_dir else curr_dir
        )

        return opts

    if opts.parse:
        opts.command = "parse"

        path = files.find(
            opts.parse,
            curr_dir,
            main="main",
            ext="py",
        )
        if path is None:
            raise SystemExit(f"Could not find module {opts.parse}.")
        opts.parse = str(path)
        opts.output_dir = str(path.parent)

        return opts

    if opts.evaluate:
        opts.command = "evaluate"

        path = files.find(
            opts.evaluate,
            curr_dir,
            main="main",
            ext="py",
        )
        if path is None:
            raise SystemExit(f"Could not find module {opts.evaluate}.")
        opts.evaluate = str(path)
        opts.output_dir = str(path.parent)

        return opts

    if opts.validate:
        opts.command = "validate"

        config_path = files.find(
            opts.init_config,
            curr_dir,
            opts.configs_dir,
            main="index",
            ext="yaml",
        )
        if config_path is None:
            raise SystemExit(f"Could not find configuration {opts.init_config}.")
        opts.init_config = str(config_path)
        opts.configs_dir = str(data_dir)

        return opts

    return opts
