import bisect
from itertools import cycle

import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick


from pandas import DataFrame

__cm_to_inch = 1/2.54


def plot_stacked_barplot(filename: str, data: dict, plot_params: dict, dpi=600):
    is_horizontal = plot_params.get('is_horizontal', True)
    label_x_delta = plot_params.get('label_x_delta', 0)

    x_lbl = plot_params.get('x_label','').format(**plot_params)
    y_lbl = plot_params.get('y_label','').format(**plot_params)
    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)

    bar_width = plot_params.get('bar_width', 0.2)
    label_fmt = plot_params.get('label_fmt', "{}")
    bar_label = plot_params.get('bar_label', "{:.2f}")

    lbl_pos  = plot_params.get('lbl_pos', (0.5, 1.1))
    lbl_ncol = plot_params.get('lbl_ncol', 3)

    labels    = sorted(data.keys())
    # Read Y tick labels from vals keys
    #v_ticks   = [ x.replace(r'_', r'\_').replace(r'%', r'\%') for x in 
    #                sorted(next(iter(xy_values.values()))['x_labels'])]
    v_ticks = sorted(data.keys())

    nbars     = len(labels)
    bar_delta = [bar_width*(x-(nbars-1)/2) for x in np.arange(nbars)]

    stacked_values = dict()
    for label in labels:
        stacked_values[label] = list()
        for linkId, events in data[label].items():
            packets_ok = events["OK"]
            packets_st = events["STALL"]
            bisect.insort_left(stacked_values[label], (packets_ok, packets_st), key=lambda x: -x[0])
    #print(stacked_values)

    fig, ax = plt.subplots(figsize=(x_dim*__cm_to_inch, y_dim*__cm_to_inch))
    bars = []
    for i, l in enumerate(labels):
        stack_d = 0
        bar_color = cycle([plt.get_cmap("tab20")(i) for i in range(20)])
        for packet_ok, packet_st in stacked_values[l]:
            plot_x = i #bar_delta[i] #i - bar_delta[i] if is_horizontal else i + bar_delta[i]
            if is_horizontal:
                bars.append(ax.barh(plot_x, packet_ok, bar_width, color=next(bar_color), left=stack_d ))
                bars.append(ax.barh(plot_x, packet_st, bar_width, color=next(bar_color), left=stack_d + packet_ok))
            else:
                bars.append(ax.bar( plot_x, packet_ok, bar_width, color=next(bar_color), bottom = stack_d))
                bars.append(ax.bar( plot_x, packet_st, bar_width, color=next(bar_color), bottom = stack_d + packet_ok))

            stack_d += packet_ok + packet_st


    #ax.legend(loc='upper center', ncol=lbl_ncol, bbox_to_anchor=lbl_pos,) #, loc='lower left')

    # Add some text for labels, title and custom x-axis tick labels, etc.

    #scale = plot_params.get('scale', None)

    if 'scale_x' in plot_params:
        ax.set_xscale(plot_params['scale_x'])
    if 'scale_y' in plot_params:
        ax.set_yscale(plot_params['scale_y'])

    if is_horizontal:
        if x_lbl:
            ax.set_xlabel(x_lbl)
        if y_lbl:
            ax.set_ylabel(y_lbl)
        ax.set_yticks(np.arange(len(v_ticks)))
        ax.set_yticklabels(v_ticks)
        ax.grid(axis='x')
        #if(scale == "log"):
        #    #xmin, xmax = ax.get_xlim()
        #    #nmax = math.pow(10, math.ceil(math.log10(xmax)))
        #    ax.set_xscale(scale)
        #    xmin, xmax = ax.get_xlim()
        #    nmin = None
        #    nmax = math.pow(10, math.ceil(math.log10(xmax)))
        #    if (xmin > 1E-6):
        #        nmin = math.pow(10, math.floor(math.log10(xmin)))
        #    ax.set_xlim(left=nmin, right=nmax)
        #if (scale == "percentage"):
        #    ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    else:
        if y_lbl:
            ax.set_xlabel(y_lbl)
        if x_lbl:
            ax.set_ylabel(x_lbl)
        ax.set_xticks(np.arange(len(v_ticks)))
        ax.set_xticklabels(v_ticks)
        ax.grid(axis='y')
        #if(scale == "log"):
        #    ax.set_yscale(scale)
        #if (scale == "percentage"):
        #    ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    #for b in bars:
    #    autolabel(b, ax, bar_label, is_horizontal=is_horizontal, label_x_delta=label_x_delta)


    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)

    return
