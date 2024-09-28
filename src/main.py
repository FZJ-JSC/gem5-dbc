#!/usr/bin/env python3
from g5dbc.manager import Options
from g5dbc.manager import generate_workload
from g5dbc.manager import parse_workload

from g5dbc.manager import read_config_file

def main():
    # Read command line options
    options = Options.parse_from_args()

    if options.generate:
        generate_workload(options)
    if options.parse:
        parse_workload(options)
    # if options.plots:
    #     generate_plots(options)

    return 0

def m5_main():
    from g5dbc.sim import simulate

    # Read command line options
    options = Options.parse_from_args()
    config = read_config_file(options)

    simulate(config)

    return 0

if __name__ == "__main__":
    main()

if __name__ == "__m5_main__":
    m5_main()