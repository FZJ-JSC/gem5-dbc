import math
import re
from pathlib import Path
from collections import defaultdict

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import write_scatterplot_hline

default_plots = [
        dict(
            suffix = "network_latency_router_to_router_network-{src}_{dst}_vnet{vnet}",
            col_regex = r"mesh_network_latencies_routers_src_dst_network_vnet(\d+)$",
            max_x   = 10000,
            x_label = r"VNET={vnet} Router {src}$\rightarrow${dst} Latency [Cycles]",
            y_label = 'Events',
        ),
        dict(
            suffix = "network_latency_router_to_router_queueing-{src}_{dst}_vnet{vnet}",
            col_regex = r"mesh_network_latencies_routers_src_dst_queueing_vnet(\d+)$",
            max_x   = 10000,
            x_label = r"VNET={vnet} Router {src}$\rightarrow${dst} Latency [Cycles]",
            y_label = 'Events',
        ),
]

def parse_xy_values(vals, strict_positive : bool = True):
    xy_values = dict()

    controllers = dict()
    for k,v in vals.items():
        (ctrl1Id,ctrl2Id,bucket) = k
        if (ctrl1Id,ctrl2Id) not in controllers:
            controllers[(ctrl1Id,ctrl2Id)] = dict()
        controllers[(ctrl1Id,ctrl2Id)].update([(bucket,v)])

    for ctrlId,events in controllers.items():
        len_x = max(events.keys()) + 1
        if strict_positive:
            xy_values[ctrlId] = dict(
                x = [i for i in range(len_x) if events.get(i,0) > 0],
                y = [events.get(i,0) for i in range(len_x) if events.get(i,0) > 0]
            )
        else:
            xy_values[ctrlId] = dict(
                x = list(range(len_x)),
                y = [events.get(i,0) for i in range(len_x)]
            )

    return xy_values


def parse_controller_values(i_col,col_regex,rows):

    sparse_cols = [c for c in rows if re.match(col_regex, c)]
    if not sparse_cols:
        print(f"Warning: column regex {col_regex} not found")
        return dict()

    dvals = dict()
    for col in sparse_cols:
        vnet = int(next(iter(re.findall(col_regex, col))))
        data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
        dvals.update([(vnet,dict())])
        for label,row in data.items():
            dvals[vnet][label] = parse_xy_values(row[col])

    nested_dict = lambda: defaultdict(nested_dict)
    xy_values = nested_dict()
    for vnet in dvals.keys():
        for label in dvals[vnet].keys():
            for router in dvals[vnet][label].keys():
                xy_values[vnet][router][label] = dvals[vnet][label][router]

    return xy_values


def sum_xy_values(xy1: dict, xy2: dict, strict_positive: bool = True):

    x1 = xy1['x']
    x2 = xy2['x']

    y1 = xy1['y']
    y2 = xy2['y']

    d1 = {x1[i]:y1[i] for i in range(len(x1))}
    d2 = {x2[i]:y2[i] for i in range(len(x2))}

    xmax = max(x1+x2) + 1

    summed_xy = dict()

    if strict_positive:
        summed_xy = dict(
            x = [i for i in range(xmax) if (d1.get(i,0) + d2.get(i,0)) > 0],
            y = [(d1.get(i,0) + d2.get(i,0)) for i in range(xmax) if (d1.get(i,0) + d2.get(i,0)) > 0]
        )
    else:
        summed_xy = dict(
            x = list(range(xmax)),
            y = [(d1.get(i,0) + d2.get(i,0)) for i in range(xmax)]
        )



    return summed_xy

def sum_over_dests(i_col,col_regex,rows):
    xy_values = parse_controller_values(i_col,col_regex,rows)

    summed_xy_values = dict()
    for vnet in xy_values.keys():
        summed_xy_values[vnet] = dict()
        for (src,dst) in xy_values[vnet].keys():
            if src not in summed_xy_values[vnet]:
                summed_xy_values[vnet][src] = dict()
            for label in xy_values[vnet][(src,dst)].keys():
                if label not in summed_xy_values[vnet][src]:
                    summed_xy_values[vnet][src][label] = dict(x=[],y=[])
                xy1 = summed_xy_values[vnet][src][label]
                xy2 = xy_values[vnet][(src,dst)][label]
                summed_xy_values[vnet][src][label] = sum_xy_values(xy1, xy2)
    return summed_xy_values


def sum_over_srcs(i_col,col_regex,rows):
    xy_values = parse_controller_values(i_col,col_regex,rows)

    summed_xy_values = dict()
    for vnet in xy_values.keys():
        summed_xy_values[vnet] = dict()

        for (src,dst) in xy_values[vnet].keys():
            if dst not in summed_xy_values[vnet]:
                summed_xy_values[vnet][dst] = dict()

            for label in xy_values[vnet][(src,dst)].keys():
                if label not in summed_xy_values[vnet][dst]:
                    summed_xy_values[vnet][dst][label] = dict(x=[],y=[])
                xy1 = summed_xy_values[vnet][dst][label]
                xy2 = xy_values[vnet][(src,dst)][label]
                summed_xy_values[vnet][dst][label] = sum_xy_values(xy1, xy2)
    return summed_xy_values


def read_column(col,i_col,rows):
    data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
    d1 = {k:v[col] for k,v in data.items() }
    return d1

def sum_events(xy_values):
    for label, events in xy_values.items():
        events['sum'] = sum(events['y'])
    return xy_values

def write_router_to_router_latency_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) > 0:
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            i_col = params['inner_col']

            col_regex = params['col_regex'].format(**p)

            xy_values = sum_over_srcs(i_col,col_regex,rows)
            for vnet in xy_values.keys():
                for dst in xy_values[vnet].keys():
                    params.update([('src',"ALL"),('dst',dst),('vnet',vnet)])
                    filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                    print(f"Writing image to {filename}")
                    data = xy_values[vnet][dst]
                    write_scatterplot(filename, data, params)

            xy_values = sum_over_dests(i_col,col_regex,rows)
            for vnet in xy_values.keys():
                for src in xy_values[vnet].keys():
                    params.update([('src',src),('dst',"ALL"),('vnet',vnet)])
                    filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                    print(f"Writing image to {filename}")
                    data = xy_values[vnet][src]
                    write_scatterplot(filename, data, params)
