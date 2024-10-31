import numpy as np
from pathlib import Path
import re

from modules.stats.readers import read_rows
from modules.graphics import plot_histogram


default_plots = [
    dict(
        value_col = "mesh_router_hops_hist_vnet0",
        suffix    = "mesh_router_hops_hist_vnet0",
        desc    = 'Network Hops VNET=0',
        x_label = 'Network Hops VNET=0',
        y_label = 'Network Hop PDF',
    ),
    dict(
        value_col = "mesh_router_hops_hist_vnet1",
        suffix    = "mesh_router_hops_hist_vnet1",
        desc    = 'Network Hops VNET=1',
        x_label = 'Network Hops VNET=1',
        y_label = 'Network Hop PDF',
    ),
    dict(
        value_col = "mesh_router_hops_hist_vnet2",
        suffix    = "mesh_router_hops_hist_vnet2",
        desc    = 'Network Hops VNET=2',
        x_label = 'Network Hops VNET=2',
        y_label = 'Network Hop PDF',
    ),
    dict(
        value_col = "mesh_router_hops_hist_vnet3",
        suffix    = "mesh_router_hops_hist_vnet3",
        desc    = 'Network Hops VNET=3',
        x_label = 'Network Hops VNET=3',
        y_label = 'Network Hop PDF',
    ),
]

__epsilon = 1e-6

def normalize_pdf(pdf: np.ndarray):
    res = pdf / pdf.sum()
    # Search from the back
    max_idx = len(res) - np.argmax(res[::-1] > __epsilon) - 1
    res = res[:max_idx]
    res[np.abs(res) < __epsilon*20] = 0
    return res


def write_histogram_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if(len(rows.index) > 0):
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            # Set inner and value columns
            i_col = params['inner_col']
            v_cols = [c for c in rows if re.match(params['value_col'], c)] 
            labels = sorted(rows[i_col].unique())

            # Initialize xy_values
            xy_values = {s:dict(y=normalize_pdf(np.nan_to_num(rows[rows[i_col]==s][v_cols].values[0]))) for s in labels}
            max_len = max([len(v['y']) for v in xy_values.values()])
            for v in xy_values.values():
                ext_len = max_len - len(v['y'])
                v['x'] = np.array(range(max_len))
                v['y'] = np.append(v['y'], np.array([0.0]*ext_len) )
            
            filename = plot_directory.joinpath(fname_fmt.format(**params))
            
            print(f"Writing histogram image {params['desc']} to {filename}")
            plot_histogram(filename, xy_values, params)

