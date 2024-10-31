from pathlib import Path

import numpy as np

from modules.graphics import plot_barplot
from modules.stats.readers import read_rows
from modules.stats.table import concatenate_columns

from modules.stats.plots.bar.default import default_plots


def write_bar_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']
    
    rows, i_col = concatenate_columns(rows, plot_params['inner_col'])
    rows, o_col = concatenate_columns(rows, plot_params['outer_col'])
    
    x_vals = sorted(rows[o_col].unique())
    labels = sorted(rows[i_col].unique())
    
    if len(rows.index) > 0:
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            rows, v_col = concatenate_columns(rows, params['value_col'])

            #i_col = params['inner_col']
            #o_col = params['outer_col']
            #v_col = params['value_col']

            # Skip if data does not contain column
            if not v_col in rows.columns:
                print(f"Warning: {v_col} not found")
                continue

            xy_data = {s:dict(vals=rows[rows[i_col]==s][[o_col,v_col]].set_index(o_col).to_dict()[v_col]) for s in labels}

            xy_values = dict()
            for k, v in xy_data.items():
                xy_values[k] = dict(
                    x_labels = x_vals,
                    x = np.arange(len(x_vals)),
                    y = [v['vals'].get(x,0) for x in x_vals]
                )
                #v['x'] = np.arange(len(x_vals))
                #v['y'] = [v['vals'].get(x,0) for x in x_vals]

            filename = plot_directory.joinpath(fname_fmt.format(**params))

            print(f"Writing image to {filename}")
            plot_barplot(filename, xy_values, params)







