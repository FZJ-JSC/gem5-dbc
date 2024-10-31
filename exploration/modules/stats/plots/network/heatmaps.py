import math
import numpy as np
import re

from pathlib import Path
from collections import defaultdict

from modules.stats.readers import read_rows
from modules.graphics import write_scatterplot
from modules.graphics import plot_stacked_barplot
#from modules.graphics import plot_heatmap
from modules.graphics import write_heatmap

router_plots = [
        dict(
            suffix = "network_routers_heatmap_{eventKey}_vnet{vnet}",
            col_regex = r"mesh_routers_assigned_vnet(\d+)$",
        ),
]

transit_stats = [
    dict(
        y_label = r"Router Traffic [bytes/cycle]",
        idxKey = "transitId",
        eventKey = "bytes_cycle",
        tile_fmt = "{label}\n{value:.2f}"
    ),
    dict(
        y_label = r"Router Switch Allocations",
        idxKey = "transitId",
        eventKey = "OK",
        tile_fmt = "{label}\n{value:.2E}"
    ),
    dict(
        y_label = r"Router Switch Stalls",
        idxKey = "transitId",
        eventKey = "ST",
        tile_fmt = "{label}\n{value:.2E}"
    ),
    dict(
        y_label = r"Router Switch Allocations [\% Total]",
        idxKey = "transitId",
        eventKey = "TR",
        tile_fmt = "{label}\n{value:.2%}"
    ),
    dict(
        y_label = r"Router Switch Allocations [1/cycle]",
        idxKey = "transitId",
        eventKey = "OK_cycle",
        tile_fmt = "{label}\n{value:.2f}"
    ),
    dict(
        y_label = r"Router Switch Stalls [1/cycle]",
        idxKey = "transitId",
        eventKey = "ST_cycle",
        tile_fmt = "{label}\n{value:.2f}"
    ),
    dict(
        y_label = r"Router Switch Stalls [\% Requests]",
        idxKey = "transitId",
        eventKey = "ST_PC",
       tile_fmt = "{label}\n{value:.2%}"
    ),
]


flit_size_bytes = 64

def read_column(col,i_col,rows):
    data = rows[[col,i_col]].set_index(i_col).transpose().to_dict()
    d1 = {k:v[col] for k,v in data.items() }
    return d1


def parse_router_values(i_col,col_regex,rows):

    out_log = read_column('output_log',i_col,rows)

    def search_item(label:str, linkId: int, direction:str = "in"):
        for i in out_log[label]["network"]["links"]:
            if i["linkId"] == abs(linkId):
                if i["linkType"] == "Internal":
                    return i
                elif i["linkType"] == "ExtIn" and direction == "in":
                    return i
                elif i["linkType"] == "ExtOut" and direction == "out":
                    return i
        return None

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
            events = list()
            for k,v in row[col].items():
                (routerId,inLink,outLink) = k
                inData  = search_item(label, inLink,  direction="in")
                outData = search_item(label, outLink, direction="out")
                events.append(dict(
                    routerId=routerId,
                    inLink=inLink,
                    outLink=outLink,
                    inData=inData,
                    outData=outData,
                    events = v
                ))

            dvals[vnet][label] = events

    #nested_dict = lambda: defaultdict(nested_dict)
    #xy_values = nested_dict()
    #for vnet in dvals.keys():
    #    for label in dvals[vnet].keys():
    #        for router in dvals[vnet][label].keys():
    #            xy_values[vnet][router][label] = dvals[vnet][label][router]

    return dvals


def read_source_destination_transit(data: list):
    events = dict()
    for event in data:
        transitId = event["routerId"]
        srcId = event["inData"]["srcId"]
        dstId = event["outData"]["destId"]

        if event["inData"]["linkType"] == "ExtIn":
            srcId += 1000
        if event["outData"]["linkType"] == "ExtOut":
            dstId += 1000

        key = (srcId,dstId,transitId)
        if key not in events:
            events[key] = dict(srcId=srcId,dstId=dstId,transitId=transitId,OK=0,ST=0)
        label = "OK" if event["outLink"] < 0 else "ST"
        events[key][label] += event["events"]
    
    event_list = sorted([v for v in events.values()], key = lambda v: v["OK"])

    return event_list


def sum_over_src_dest(data, cycles = 1, f = lambda x: True):

    #total_events = 0
    #for event in data:
    #    total_events += event["OK"]
    
    #print("data=", data)
    #print("total_events=", total_events)

    events = dict()
    for event in data:
        transitId = event["transitId"]
        key = transitId
        if key not in events:
            events[key] = dict(transitId=transitId,OK=0,ST=0)
        events[key]["OK"] += event["OK"]
        events[key]["ST"] += event["ST"]

    event_list = sorted([v for v in events.values() if f(v)], key = lambda v: v["OK"])
    total_events= 0
    for event in event_list:
        total_events += event["OK"]

    #print("event_list=", event_list)
    #print("total_events=", total_events)

    for event in event_list:
        event["TR"] = float(event["OK"])/total_events
        event["ST_PC"] = float(event["ST"])/(event["OK"]+event["ST"])
        event["OK_cycle"] = float(event["OK"])/cycles
        event["ST_cycle"] = float(event["ST"])/cycles
        event["bytes_cycle"] = flit_size_bytes*float(event["OK"])/cycles

    return event_list


def sum_over_transit(data, cycles = 1):
    events = dict()

    total_events = 0
    for event in data:
        total_events += event["OK"]

    for event in data:
        srcId=event["srcId"]
        dstId=event["dstId"]
        key = (srcId,dstId)
        if key not in events:
            events[key] = dict(srcId=srcId,dstId=dstId,OK=0,ST=0)
        events[key]["OK"] += event["OK"]
        events[key]["ST"] += event["ST"]

    event_list = sorted([v for v in events.values()], key = lambda v: v["OK"])

    for event in event_list:
        event["TR"] = float(event["OK"])/total_events
        event["ST_PC"] = float(event["ST"])/(event["OK"]+event["ST"])
        event["OK_cycle"] = float(event["OK"])/cycles
        event["ST_cycle"] = float(event["ST"])/cycles
        event["bytes_cycle"] = flit_size_bytes*float(event["OK"])/cycles

    return event_list


def get_router_label(label,i):
    rl = f"R{i:02d}\n "
    if label.startswith("T1"):
        if i == 0 or i == 4 or i == 8 or i == 12:
            rl = f"R{i:02d}\n(2MEM)"
        if 1 <= i and i < 4:
            rl = f"R{i:02d}\n(2C2S)"
        if 5 <= i and i < 8:
            rl = f"R{i:02d}\n(2C2S)"
        if 10 <= i and i < 12:
            rl = f"R{i:02d}\n(2C2S)"
    if label.startswith("T2"):
        if i == 0 or i == 4 or i == 8 or i == 12:
            rl = f"R{i:02d}\n(2MEM)"
        if i == 1 or i == 5 or i == 9 or i == 13:
            rl = f"R{i:02d}\n(4SLC)"
        if i == 2 or i == 6 or i == 10 or i == 11:
            rl = f"R{i:02d}\n(4CPU)"
    if label.startswith("T3"):
        if i == 0 or i == 4 or i == 8 or i == 12:
            rl = f"R{i:02d}\n(2MEM)"
        if i == 1 or i == 5 or i == 9 or i == 13:
            rl = f"R{i:02d}\n(4CPU)"
        if i == 6 or i == 7 or i == 10 or i == 11:
            rl = f"R{i:02d}\n(4SLC)"
    return rl

def get_heatmap_xy_values(events: list, idxKey: str, valKey: str, label:str, minIdx = 0, maxIdx = 0, n_rows = 4, n_cols = 4):
    event_map = {e[idxKey] : e[valKey] for e in events }
    if maxIdx == 0:
        maxIdx = max(event_map.keys())+1

    event_list = [event_map.get(i,0) for i in range(minIdx,maxIdx)]

    labels = np.flip(np.reshape([get_router_label(label,i) for i in range(minIdx,maxIdx) ], (n_rows, n_cols)),0)
    values = np.flip(np.reshape([np.nan_to_num(event_list[i]) for i in range(maxIdx-minIdx) ], (n_rows, n_cols)),0)

    xy_values = dict(
                values = values,
                labels =labels
            )
    return xy_values

def write_network_heatmaps(data_directory: Path, plot_directory: Path, select_rows: dict, plot_params: dict, extra_plots = []):
    rows = read_rows(data_directory, select_rows)
    fname_fmt  = plot_params['fname_fmt']

    if len(rows.index) < 1:
        return

    for p in [*router_plots, *extra_plots]:
        # Merge all parameters
        params = {**select_rows, **plot_params, **p}

        i_col = params['inner_col']
        col_regex = params['col_regex'].format(**p)

        data = parse_router_values(i_col,col_regex,rows)
        cycles = read_column('cycles',i_col,rows)


        for vnet, items in data.items():
            #if vnet != 0:
            #    continue
            for label, events in sorted(items.items()):
            #    if label != "T1-n1" and label != "T1-n2" and label != "T1-n0" :
            #        continue

                minIdx=0
                maxIdx=16

                #print(label, events)

                src_dest_transit_list = read_source_destination_transit(events)

                for stats in transit_stats:
                    transit_list = sum_over_src_dest(
                        src_dest_transit_list,
                        cycles = cycles[label],
                        f = lambda x: minIdx <= x[stats["idxKey"]] and x[stats["idxKey"]] < maxIdx)

                    xy_values = get_heatmap_xy_values(
                        transit_list, stats["idxKey"], stats["eventKey"], label, minIdx=minIdx,maxIdx=maxIdx)

                    params.update([
                        ('y_label',  stats["y_label"]),
                        ('tile_fmt', stats.get("tile_fmt", "{label}\n{value:.2E}")),
                        ('title', params.get("title_fmt", "").format(label=label) ),
                        ('eventKey', stats["eventKey"]),
                        ('vnet',vnet),
                        ('label',f"{label}_{maxIdx}")
                    ])
                    filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
                    print(f"Writing image to {filename}")
                    #print("transit_list=", transit_list)
                    #print(xy_values)
                    
                    #for i in transit_list:
                    #    print("label={} router={} OK={} ST={} ST_PC={}".format(label, i["transitId"], i["OK"], i["ST"], i["ST_PC"]))

                    write_heatmap(filename, xy_values, params)


        #        params.update([('src',routerId),('vnet',vnet)])
        #        filename = plot_directory.joinpath(fname_fmt.format(**params).format(**params))
        #        print(f"Writing image to {filename}")
        #        data = asignment[routerId]
        #        print(data)
                #plot_stacked_barplot(filename, data, params)
