
import matplotlib.pyplot as plt
import numpy as np
import math

from modules.graphics.colormaps import categorical_colormap


__cm_to_inch = 1/2.54

def get_color_index(ncol: int):
    clr_idx = []
    if ncol<=4:
        for i in range(4):
            for j in range(ncol):
                clr_idx.append(i*4+j)
    else:
        clr_idx = list(range(40))

    return iter([plt.get_cmap("tab20c")(i) for i in clr_idx])


def write_scatterplot(filename: str, xy_values: dict, plot_params: dict, dpi=600):

    x_lbl = plot_params['x_label'].format(**plot_params)
    y_lbl = plot_params['y_label'].format(**plot_params)
    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)

    lbl_pos  = plot_params.get('lbl_pos', (0.5, 1.1))
    lbl_ncol = plot_params.get('lbl_ncol', 3)

    title = plot_params.get('title','').replace(r'_', r'\_').replace(r'%', r'\%')
    max_x = plot_params.get('max_x', None)

    labels     = sorted(xy_values.keys())

    fig, ax = plt.subplots(figsize=(x_dim*__cm_to_inch, y_dim*__cm_to_inch))

    #line_color = get_color_index(lbl_ncol)
    cmap = categorical_colormap(lbl_ncol, math.ceil(len(labels) / lbl_ncol) )
    line_color = iter([cmap(i) for i in range(len(labels))])
    for label in labels: #, values in xy_values.items():
        v = xy_values[label]
        x = v['x'][:max_x] if max_x else v['x']
        y = v['y'][:max_x] if max_x else v['y']
        if plot_params.get("scale_x",None) == "log":
            x = [1e-1 if v == 0 else v for v in x]
        ax.plot(x, y, '-', color=next(line_color), label=label)

    ax.set_title(title)
    ax.set_xlabel(x_lbl)
    ax.set_ylabel(y_lbl)

    if 'scale_x' in plot_params:
        ax.set_xscale(plot_params['scale_x'])
    if 'scale_y' in plot_params:
        ax.set_yscale(plot_params['scale_y'])

    ax.legend(loc='upper center', ncol=lbl_ncol, bbox_to_anchor=lbl_pos,) #, loc='lower left')
    ax.minorticks_on()
    ax.grid(axis='x', which="both")
    ax.grid(axis='y', which="both")

    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)


    return
