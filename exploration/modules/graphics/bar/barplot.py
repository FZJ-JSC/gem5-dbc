import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

from pandas import DataFrame

__cm_to_inch = 1/2.54

# matplotlib code taken from 
# https://matplotlib.org/3.1.1/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py

def autolabel(rects, ax, labelfmt="{:.2f}", is_horizontal=True, label_x_delta = 0):
    for rect in rects:
        wdth = rect.get_width()
        hght = rect.get_height()
        posx = rect.get_x()
        posy = rect.get_y()
        ha='center'
        if is_horizontal:
            x = label_x_delta + 0.8*wdth 
            y = posy+0.5*hght
            v ='center'
            label = " " + labelfmt.format(wdth).replace(r'_', r'\_').replace(r'%', r'\%')
        else:
            x = posx + wdth / 2
            y = 0.95*hght
            v ='top'
            label = " " + labelfmt.format(hght).replace(r'_', r'\_').replace(r'%', r'\%')
        
        ax.annotate( label, xy= (x,y), ha=ha, va=v)


def plot_barplot(filename: str, xy_values: dict, plot_params: dict, dpi=600):

    is_horizontal = plot_params.get('is_horizontal', True)
    label_x_delta = plot_params.get('label_x_delta', 0)

    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)

    bar_width = plot_params.get('bar_width', 0.2)
    label_fmt = plot_params.get('label_fmt', "{}")
    bar_label = plot_params.get('bar_label', "{:.2f}")

    lbl_pos  = plot_params.get('lbl_pos', (0.5, 1.1))
    lbl_ncol = plot_params.get('lbl_ncol', 3)

    labels    = sorted(xy_values.keys())
    # Read Y tick labels from vals keys
    v_ticks   = [ x.replace(r'_', r'\_').replace(r'%', r'\%') for x in 
                    sorted(next(iter(xy_values.values()))['x_labels'])]
    nbars     = len(labels)
    bar_delta = [bar_width*(x-(nbars-1)/2) for x in np.arange(nbars)]
    #bar_color = [plt.get_cmap("Blues")(x)  for x in np.linspace(0.3,0.7,nbars)]
    bar_color = iter([plt.get_cmap("tab20")(i) for i in range(40)])


    fig, ax = plt.subplots(figsize=(x_dim*__cm_to_inch, y_dim*__cm_to_inch))
    bars = []
    for i, l in enumerate(labels):
        x = xy_values[l]['x']
        y = xy_values[l]['y']
        plot_x = x - bar_delta[i] if is_horizontal else x + bar_delta[i]
        plot_y = y
        label = label_fmt.format(l).replace(r'_', r'\_').replace(r'%', r'\%')
        if is_horizontal:
            bars.append(ax.barh(plot_x, plot_y, bar_width, color=next(bar_color), label=label ))
        else:
            bars.append(ax.bar( plot_x, plot_y, bar_width, color=next(bar_color), label=label ))

    ax.legend(loc='upper center', ncol=lbl_ncol, bbox_to_anchor=lbl_pos,) #, loc='lower left')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    x_lbl = plot_params.get('x_label', None)
    y_lbl = plot_params.get('y_label', None)
    scale = plot_params.get('scale', None)

    if is_horizontal:
        if x_lbl:
            ax.set_xlabel(x_lbl)
        if y_lbl:
            ax.set_ylabel(y_lbl)
        ax.set_yticks(np.arange(len(v_ticks)))
        ax.set_yticklabels(v_ticks)
        ax.grid(axis='x')
        if(scale == "log"):
            #xmin, xmax = ax.get_xlim()
            #nmax = math.pow(10, math.ceil(math.log10(xmax)))
            ax.set_xscale(scale)
            xmin, xmax = ax.get_xlim()
            nmin = None
            nmax = math.pow(10, math.ceil(math.log10(xmax)))
            if (xmin > 1E-6):
                nmin = math.pow(10, math.floor(math.log10(xmin)))
            ax.set_xlim(left=nmin, right=nmax)
        if (scale == "percentage"):
            ax.xaxis.set_major_formatter(mtick.PercentFormatter(1.0))
    else:
        if y_lbl:
            ax.set_xlabel(y_lbl)
        if x_lbl:
            ax.set_ylabel(x_lbl)
        ax.set_xticks(np.arange(len(v_ticks)))
        ax.set_xticklabels(v_ticks)
        ax.grid(axis='y')
        if(scale == "log"):
            ax.set_yscale(scale)
        if (scale == "percentage"):
            ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))

    for b in bars:
        autolabel(b, ax, bar_label, is_horizontal=is_horizontal, label_x_delta=label_x_delta)

    #ax.set_title(title)

    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)


    return
