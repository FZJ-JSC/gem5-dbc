import math
import re
import numpy as np
from pathlib import Path

from modules.stats.readers import read_rows
from modules.graphics import write_heatmap


default_plots = [
    dict(
        suffix = "router_reads_flits_cycles",
        y_label = "Router Reads [flits/cycle]",
        title = "",
        tile_fmt = "{label}\n{value:.2f}",
        col_regex = r"network_router(\d+)_reads_flits_per_cycle$",
    ),
    dict(
        suffix = "router_reads_flits",
        y_label = "Router Reads [flits]",
        title = "",
        tile_fmt = "{label}\n{value:.2E}",
        col_regex = r"network_router(\d+)_reads_flits$",
    ),
    dict(
        suffix = "router_reads_bytes_cycles",
        y_label = "Router Reads [bytes/cycle]",
        title = "",
        tile_fmt = "{label}\n{value:.2f}",
        col_regex = r"network_router(\d+)_reads_bytes_per_cycle$",
    ),
    dict(
        suffix = "router_reads_bytes",
        y_label = "Router Reads [bytes]",
        title = "",
        tile_fmt = "{label}\n{value:.2E}",
        col_regex = r"network_router(\d+)_reads_bytes$",
    ),
]

def get_default_router_labels(n_rows = 4, n_cols = 4 ):
     
    n_vals = [f"R{i:02d}" for i in range(n_rows*n_cols) ]

    a = np.flip(np.reshape(n_vals, (n_rows, n_cols)),0)
    
    return a

def get_default_topology_heatmap(data: dict, n_rows = 4, n_cols = 4 ):

    n_rows = 4
    n_cols = 4
    n_vals = [np.nan_to_num(data[i]) for i in range(n_rows*n_cols) ]

    a = np.flip(np.reshape(n_vals, (n_rows, n_cols)),0)
    
    return a

def write_heatmap_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if(len(rows.index) != 1):
        print(f"write_heatmap_plots: row is not unique")
    else:
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            regex = params['col_regex']
            r_cols = [c for c in rows if re.match(regex, c)]

            if not r_cols:
                print(f"Warning: {regex} not found")
                continue

            res = list(rows[r_cols].transpose().to_dict().values())[0]
            data = {int(re.findall(regex,k)[0]):v for k,v in res.items()}

            xy_values = dict(
                values = get_default_topology_heatmap(data),
                labels = get_default_router_labels()
            )

            filename = plot_directory.joinpath(fname_fmt.format(**params))

            print(f"Writing image to {filename}")
            write_heatmap(filename, xy_values, params)

    return