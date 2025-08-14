from pathlib import Path

from platformdirs import user_config_dir, user_data_dir

from .manager import (
    evaluate_results,
    generate_artifact_index,
    generate_workload,
    options,
    parse_workload,
    resource_add,
    resource_del,
    validate_config,
)


def main():
    appname = "gem5-dbc"

    conf_dir = Path(user_config_dir(appname))
    data_dir = Path(user_data_dir(appname))

    # Create local user configuration directory if it does not exist
    if not conf_dir.exists():
        conf_dir.mkdir(parents=True, exist_ok=True)

    # Read command line options
    opts = options.from_args(
        conf_dir=conf_dir,
        data_dir=data_dir,
    )

    # Match command
    match opts.command:
        case "resource_add":
            resource_add(opts)
        case "resource_del":
            resource_del(opts)
        case "generate":
            generate_workload(opts)
        case "parse":
            parse_workload(opts)
        case "evaluate":
            evaluate_results(opts)
        case "validate":
            validate_config(opts)
        case "generate_index_se":
            generate_artifact_index(opts)
        case _:
            print("Please specify a command to execute. Use --help for more details.")

    return 0
