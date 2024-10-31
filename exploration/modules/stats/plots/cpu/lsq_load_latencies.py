import math
import re
from pathlib import Path
from collections import defaultdict

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import write_scatterplot_hline


default_plots = [
    dict(
       suffix = "CPU_loadToUse",
       col_regex = r"CPU_loadToUse",
       max_x   = 50000,
       x_label = 'CPU Load Latency [Cycles]',
       y_label = 'Events',
    ),
]

def parse_lsq_values(i_col,col,rows):
    data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()

    #print("data", data)

    res = dict()
    for label,row in data.items():
        events = dict()
        for k,v in row[col].items():
            (cpuId,bucket) = k
            if cpuId not in events:
                events[cpuId] = dict()
            events[cpuId].update([(bucket,v)])
        res[label] = events

    return res


def sum_over_cpus(data: dict):
    res = dict()

    for label,events in data.items():
        summed = dict()
        for cpuId,buckets in events.items():
            for bucket,nevents in buckets.items():
                if bucket not in summed:
                    summed[bucket] = 0
                summed[bucket] += nevents
        res[label] = summed

    return res

def parse_xy_values(data: dict, min_x=10, max_x=None):
    res = dict()

    for label, events in data.items():
        if not max_x:
            max_x = max(events.keys()) + 1
        res[label] = dict(
            x = [i for i in range(min_x, max_x) if events.get(i,0) > 0],
            y = [events.get(i,0) for i in range(min_x, max_x) if events.get(i,0) > 0]
        )

    return res


def write_lsq_load_latencies_plot(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) < 1:
        return

    for p in [*default_plots, *extra_plots]:
        # Merge all parameters
        params = {**select_rows, **plot_params, **p}

        i_col = params['inner_col']

        col_regex = params['col_regex'].format(**p)

        #cycles = read_column('cycles',i_col,rows)

        data = parse_lsq_values(i_col,col_regex,rows)
        #print("data",data)

        summed = sum_over_cpus(data)
        #print("summed",summed)

        xy_values = parse_xy_values(summed)
        #print("xy_values",xy_values)

        filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
        print(f"Writing image to {filename}")
        write_scatterplot(filename, xy_values, params)

        #for vnet, assignment in assignments.items():
        #    for ni in sorted(assignment.keys()):
        #        #params.update([('src',ni),('vnet',vnet)])
        #        filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
        #        print(f"Writing image to {filename}")
        #        data = assignment[ni]
        #        plot_stacked_barplot(filename, data, params)
