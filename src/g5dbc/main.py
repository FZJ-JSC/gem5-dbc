from platformdirs import user_config_dir, user_data_dir

from .manager import (
    Options,
    configure_resources,
    generate_workload,
    parse_workload,
    validate_config,
)


def main():
    appname = "gem5-dbc"
    # Read command line options
    options = Options.parse_from_args(user_config_dir(appname), user_data_dir(appname))
    # Match command
    match options.command:
        case "resource_add":
            configure_resources("add", options)
        case "resource_del":
            configure_resources("del", options)
        case "generate":
            generate_workload(options)
        case "parse":
            parse_workload(options)
        case "validate":
            validate_config(options)
        case _:
            print("Please specify a command to execute. Use --help for more details.")

    return 0
