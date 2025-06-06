from platformdirs import user_config_dir, user_data_dir

from .manager import (
    evaluate_results,
    generate_workload,
    options,
    parse_workload,
    resource_add,
    resource_del,
    validate_config,
)


def main():
    appname = "gem5-dbc"

    # Read command line options
    opts = options.from_args(
        user_conf_dir=user_config_dir(appname),
        user_data_dir=user_data_dir(appname),
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
        case _:
            print("Please specify a command to execute. Use --help for more details.")

    return 0
