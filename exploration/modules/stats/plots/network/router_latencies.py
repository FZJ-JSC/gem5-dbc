from curses.ascii import ctrl
import math
import re
from pathlib import Path
from collections import defaultdict

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import write_scatterplot_hline


def get_ctrl_label(ctrlId: int):
    label = ""
    if ctrlId < 32:
        cpuId = ctrlId // 2
        l1 = "L1D" if ctrlId % 2 == 1 else "L1I"
        label = f"CPU={cpuId} {l1}"
    if 32 <= ctrlId and ctrlId < 48:
        cpuId = ctrlId - 32
        label = f"CPU={cpuId} L2"
    if 48 <= ctrlId and ctrlId < 64:
        slcId = ctrlId - 48
        label = f"SLC={slcId}"
    if 67 <= ctrlId and ctrlId < 75:
        memId = ctrlId - 67
        label = f"MEM={memId}"
    return label



default_plots = [
    dict(
       suffix = "network_latency_ni_src_delay-{ctrl:02d}_vnet{vnet}",
       col_regex = r"mesh_network_latencies_ni_src_delay_vnet(\d+)_nis$",
       max_x   = 10000,
       x_label = 'VNET={vnet} {ni_label} Source Injection Latency [Cycles]',
       y_label = 'Events',
    ),
    dict(
        suffix = "network_latency_router-{ctrl:02d}_vnet{vnet}",
        col_regex = r"mesh_network_latencies_vnet(\d+)_router$",
        max_x   = 10000,
        x_label = 'VNET={vnet} Router={ctrl:02d} Latency [Cycles]',
        y_label = 'Events',
    ),
]

def parse_xy_values(vals, strict_positive : bool = True):
    xy_values = dict()

    controllers = dict()
    for k,v in vals.items():
        (ctrlId,bucket) = k
        if ctrlId not in controllers:
            controllers[ctrlId] = dict()
        controllers[ctrlId].update([(bucket,v)])

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
                xy_values[router][vnet][label] = dvals[vnet][label][router]

    return xy_values
     
def read_column(col,i_col,rows):
    data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
    d1 = {k:v[col] for k,v in data.items() }
    return d1

def sum_events(xy_values):
    for label, events in xy_values.items():
        events['sum'] = sum(events['y'])
    return xy_values

def write_router_latency_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']


    if len(rows.index) > 0:
        for p in [*default_plots, *extra_plots]:
            # Merge all parameters
            params = {**select_rows, **plot_params, **p}

            i_col = params['inner_col']

            col_regex = params['col_regex'].format(**p)

            cycles = read_column('cycles',i_col,rows)

            xy_values = parse_controller_values(i_col,col_regex,rows)

            for ctrl in xy_values.keys():
                for vnet in xy_values[ctrl].keys():
                    params.update([('ctrl',ctrl),('vnet',vnet),('ni_label',get_ctrl_label(ctrl))])

                    data = xy_values[ctrl][vnet]

                    filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                    print(f"Writing image to {filename}")
                    write_scatterplot(filename, data, params)
