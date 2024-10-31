import math
from os import link
import re
from pathlib import Path
from collections import defaultdict

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import plot_stacked_barplot

router_plots = [
        dict(
            suffix = "network_routers_assigned-{src:02d}_vnet{vnet}",
            col_regex = r"mesh_routers_assigned_vnet(\d+)$",
            max_x   = 100,
            x_label = 'VNET={vnet} Router={src:02d} Link Assignments',
            #y_label = 'Events',
        ), ]
niface_plots = [
        dict(
            suffix = "network_net_ifs_assigned-{src:02d}_vnet{vnet}",
            col_regex = r"mesh_net_ifs_assigned_vnet(\d+)$",
            max_x   = 100,
            x_label = 'VNET={vnet} NI={src:02d} Link Assignments',
            #y_label = 'Events',
        ),
]

def read_column(col,i_col,rows):
    data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
    d1 = {k:v[col] for k,v in data.items() }
    return d1

def parse_router_values(i_col,col_regex,rows):

    sparse_cols = [c for c in rows if re.match(col_regex, c)]
    if not sparse_cols:
        print(f"Warning: column regex {col_regex} not found")
        return dict()

    dvals = dict()
    for col in sparse_cols:
        # read vnet from regexp
        vnet = int(next(iter(re.findall(col_regex, col))))
        data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
        dvals.update([(vnet,dict())])
        for label,row in data.items():
            controllers = dict()
            for k,v in row[col].items():
                (routerId,linkId,bucket) = k
                if routerId not in controllers:
                    controllers[routerId] = dict()
                if linkId not in controllers[routerId]:
                    controllers[routerId][linkId] = dict()
                controllers[routerId][linkId].update([(bucket,v)])

            dvals[vnet][label] = controllers

    #nested_dict = lambda: defaultdict(nested_dict)
    #xy_values = nested_dict()
    #for vnet in dvals.keys():
    #    for label in dvals[vnet].keys():
    #        for router in dvals[vnet][label].keys():
    #            xy_values[vnet][router][label] = dvals[vnet][label][router]

    return dvals


def sum_over_links(data: dict):
    summed = dict()
    for inLinkId in data.keys():
        for outLinkId, v in data[inLinkId].items():
            if abs(outLinkId) not in summed:
                summed[abs(outLinkId)] = dict([("OK",0),("STALL",0)])
            key = "OK" if outLinkId >= 0 else "STALL"
            summed[abs(outLinkId)][key] += v
    return summed

def sum_assignments_over_links(i_col,col_regex,rows):
    data = parse_router_values(i_col,col_regex,rows)

    summed = dict()

    for vnet in data.keys():
        summed[vnet] = dict()
        for label in data[vnet].keys():
            #summed[vnet][label] = dict()
            for routerId, events in data[vnet][label].items():
                if routerId not in summed[vnet]:
                    summed[vnet][routerId] = dict()
                summed[vnet][routerId][label] = sum_over_links(events)
    
    return summed



def parse_niface_values(i_col,col_regex,rows):

    sparse_cols = [c for c in rows if re.match(col_regex, c)]
    if not sparse_cols:
        print(f"Warning: column regex {col_regex} not found")
        return dict()

    dvals = dict()
    for col in sparse_cols:
        # read vnet from regexp
        vnet = int(next(iter(re.findall(col_regex, col))))
        data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
        dvals.update([(vnet,dict())])
        for label,row in data.items():
            controllers = dict()
            for k,v in row[col].items():
                (ni,bucket) = k
                if ni not in controllers:
                    controllers[ni] = dict()
                controllers[ni].update([(bucket,v)])

            dvals[vnet][label] = controllers
    return dvals


def sum_over_ports(data: dict):
    summed = dict() #
    for portId, v in data.items():
        if portId not in summed:
            summed[portId] = dict([("OK",0),("STALL",0)])
        key = "OK" if portId >= 0 else "STALL"
        summed[portId][key] += v
    return summed

def sum_assignments_over_ports(i_col,col_regex,rows):
    data = parse_niface_values(i_col,col_regex,rows)

    summed = dict()

    for vnet in data.keys():
        summed[vnet] = dict()
        for label in data[vnet].keys():
            for ni, events in data[vnet][label].items():
                if ni not in summed[vnet]:
                    summed[vnet][ni] = dict()
                summed[vnet][ni][label] = sum_over_ports(events)
    
    return summed

def write_router_assignment_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) < 1:
        return

    for p in [*router_plots, *extra_plots]:
        # Merge all parameters
        params = {**select_rows, **plot_params, **p}

        i_col = params['inner_col']

        col_regex = params['col_regex'].format(**p)

        cycles = read_column('cycles',i_col,rows)

        assignments = sum_assignments_over_links(i_col,col_regex,rows)

        for vnet, asignment in assignments.items():
            for routerId in sorted(asignment.keys()):
                params.update([('src',routerId),('vnet',vnet)])
                filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                print(f"Writing image to {filename}")
                data = asignment[routerId]
                print(data)
                #plot_stacked_barplot(filename, data, params)

def write_niface_assignment_plots(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) < 1:
        return

    for p in [*niface_plots, *extra_plots]:
        # Merge all parameters
        params = {**select_rows, **plot_params, **p}

        i_col = params['inner_col']

        col_regex = params['col_regex'].format(**p)

        cycles = read_column('cycles',i_col,rows)

        assignments = sum_assignments_over_ports(i_col,col_regex,rows)

        for vnet, assignment in assignments.items():
            for ni in sorted(assignment.keys()):
                params.update([('src',ni),('vnet',vnet)])
                filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                print(f"Writing image to {filename}")
                data = assignment[ni]
                plot_stacked_barplot(filename, data, params)
