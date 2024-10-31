from pandas import DataFrame
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import math
import re

__tol = 5e-4

def get_noc_labels_24():
    num_cpus = 8
    num_routers = 16 + num_cpus
    memory_routers = [0,4,8,12]
    slc_routers    = [1,2,3, 5, 6, 7, 10, 11]
    core_routers   = [16, 17, 18, 19, 20, 21, 22, 23]
    colormap = dict(
        [(k,"red") for k in memory_routers] + 
        [(k,"blue") for k in slc_routers] +
        [(k,"green") for k in core_routers]
        )

    router_labels = [
        "M 0,4", "SLC 0", "SLC 1", "SLC 2",
        "M 1,5", "SLC 3", "SLC 4", "SLC 5",
        "M 2,6", "R9",    "SLC 6", "SLC 7",
        "M 3,7", "R13",   "R14",   "R15"]
    core_labels   = [f"CPU{idx}"  for idx in range(num_cpus)]
    labels = router_labels + core_labels + router_labels + core_labels
    colors = 2*[colormap.get(idx, "grey") for idx in range(num_routers)]
    return (labels, colors)


def get_noc_labels_32():
    num_cpus = 16
    num_routers = 16+num_cpus
    memory_routers = [0,4,8,12]
    slc_routers    = [1,2,3, 5, 6, 7, 10, 11]
    core_routers   = [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31]
    colormap = dict(
        [(k,"red") for k in memory_routers] + 
        [(k,"blue") for k in slc_routers] +
        [(k,"green") for k in core_routers]
        )

    #router_labels = [f"R{idx}"    for idx in range(4*4)]
    router_labels = [
        "M 0,4", "SLC 0,1", "SLC 2,3", "SLC 4,5",
        "M 1,5", "SLC 6,7", "SLC 8,9", "SLC 10,11",
        "M 2,6", "R9", "SLC 12,13", "SLC 14,15",
        "M 3,7", "R13", "R14", "R15"]
    core_labels   = [f"CPU{idx}"  for idx in range(num_cpus)]
    labels = router_labels + core_labels + router_labels + core_labels
    colors = 2*[colormap.get(idx, "grey") for idx in range(num_routers)]
    return (labels, colors)




def get_noc_labels(num_routers: int):
    (labels, colors) = (None,None)

    if(num_routers==24):
        (labels, colors) = get_noc_labels_24()
    if(num_routers==32):
        (labels, colors) = get_noc_labels_32()   
    
    return (labels, colors)
    
def write_sankey(rows: DataFrame, plot_params: dict, directory: Path, dpi=600):
    import plotly
    import plotly.graph_objects as go

    src_dst = plot_params['value_col']
    slf_dst = plot_params['self_dest']
    title   = plot_params['desc']
    filefmt = plot_params['filefmt']

    filename= directory.joinpath(filefmt.format(**plot_params))

    cols = [c for c in rows if re.match(src_dst, c)]
    vals = rows[cols].values[0]

    first_nan = np.argmax(np.isnan(vals[0]))
    ncols = first_nan if first_nan > 0 else len(vals)
    data = vals[:ncols]
    num_elems = math.isqrt(ncols)

    if(slf_dst):
        total = data.sum()
    else:
        for i in range(num_elems):
            data[i + i*num_elems] = 0.0
        total = data.sum()
    
    data = data / total
    data[data < __tol] = 0.0

    source = [idx % num_elems   for idx in range(ncols)]
    target = [num_elems + (idx //num_elems)  for idx in range(ncols)]

    labels, colors = get_noc_labels(num_elems)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
            pad = 10,
            thickness = 10,
            line = dict(color = "black", width = 0.5),
            label = labels,
            color = colors,
            ),
        link = dict(
            source = source,
            target = target,
            value =  data
        ))])
    fig.update_layout(
        title_text=title.format(total),
        font=dict(size = 10), # color = 'gray'),
        title_x=0.5, title_y=0.01,
        margin=dict(l=10,r=10,t=10,b=20)
    )
    
    print(f"Writing Sankey plot to {filename}")
    fig.write_image(str(filename), engine="kaleido")

