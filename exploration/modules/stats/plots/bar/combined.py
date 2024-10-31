from pathlib import Path
from functools import reduce

import numpy as np

from modules.graphics import plot_barplot
from modules.stats.readers import read_rows



def write_combined_bar_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if(len(rows.index) > 0):
        for p in [*combined_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            i_col = params['inner_col']
            x_dict = dict(params['outer_value_cols'])
            o_cols = sorted(x_dict.values())
            x_vals = sorted(x_dict.keys())
            labels = sorted(rows[i_col].unique())

            # Skip if data does not contain column
            if not reduce(lambda x, y: x and y, [v_col in rows.columns for v_col in o_cols]):
                print(f"Warning: {o_cols} not found")
                return

            xy_data = {s:dict(vals =rows[rows[i_col]==s][[i_col]+o_cols].set_index(i_col).transpose().to_dict()[s]) for s in labels}

            xy_values = dict()
            for k,v in xy_data.items():
                xy_values[k] = dict(
                    x_labels = x_vals,
                    x = np.arange(len(x_vals)),
                    y = [v['vals'].get(x_dict[x],0) for x in x_vals],
                )
                #xy_v['x'] = np.arange(len(x_vals))
                #xy_v['y'] = [v['vals'].get(x_dict[x],0) for x in x_vals]

            filename = plot_directory.joinpath(fname_fmt.format(**params))

            print(f"Writing image to {filename}")
            plot_barplot(filename, xy_values, params)
