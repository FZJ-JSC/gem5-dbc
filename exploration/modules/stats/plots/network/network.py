import math
import re
from pathlib import Path

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import plot_histogram

from modules.stats.plots.network.default import default_plots


def write_network_latency_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    #print("rows",rows)

    if(len(rows.index) > 0):
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}
            
            i_col = params['inner_col']
            strict_positive = params.get("strict_positive", True)

            col_regex = params['col_regex'].format(**p)
            # Set max_x
            params['max_x']   = params.get("max_{}".format(p['name']), params['max_x'])
            params['x_label'] = params['x_label'].format(**p)
            params['y_label'] = params['y_label'].format(**p)


            sparse_cols = [c for c in rows if re.match(col_regex, c)]
            if not sparse_cols:
                print(f"Warning: column regex {col_regex} not found")
                continue

            # Read sparse data
            data = rows[sparse_cols+[i_col]].set_index(i_col).transpose().to_dict()

            xy_values = dict()
            for label, values in data.items():
                events = {int(next(iter( re.findall(col_regex, col) or []), 0)):v for col, v in values.items() if math.isfinite(v)}
                # Length x
                min_x = params.get("min_x",1)
                max_x = max(events.keys()) + 1
                # produce coordinates for scatter plot
                if strict_positive:
                    xy_values[label] = dict(
                        x = [i for i in range(min_x,max_x) if events.get(i,0) > 0],
                        y = [events.get(i,0) for i in range(min_x,max_x) if events.get(i,0) > 0]
                    )
                else:
                    xy_values[label] = dict(
                        x = [i for i in range(min_x,max_x)],
                        y = [events.get(i,0) for i in range(min_x,max_x)]
                    )
                # if params['strictly_positive']:
                #     for k,v in xy_values.items():
                #         if v <= 0:
                #             del xy_values[k]

            filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))

            print(f"Writing image to {filename}")

            write_scatterplot(filename, xy_values, params)
