
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mtick

import numpy as np

__CM_TO_INCH = 1/2.54

def add_label(violin, label):
    """
    https://stackoverflow.com/a/58324984
    """
    color = violin["bodies"][0].get_facecolor().flatten()
    return (mpatches.Patch(color=color), label)


def write_violinplot(filename: str, xy_values: dict, plot_params: dict, dpi=600):
    """
    Write violin plots
    """

    x_lbl = plot_params['x_label']
    y_lbl = plot_params['y_label']
    label_prefix = plot_params.get('label_prefix', '')
    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)

    lbl_pos  = plot_params.get('lbl_pos', (0.5, 1.1))
    lbl_ncol = plot_params.get('lbl_ncol', 3)

    title = plot_params.get('title','').replace(r'_', r' ').replace(r'%', r'\%')
    max_x = plot_params.get('max_x', None)

    labels     = sorted(xy_values.keys())
    line_color = iter([plt.get_cmap("tab20")(i) for i in range(40)])

    v_ticks = list(map(lambda x: x.replace(r'_', r' ').replace(r'%', r'\%'), sorted(next(iter(xy_values.values()))['x_labels'])))

    fig, ax = plt.subplots(figsize=(x_dim*__CM_TO_INCH, y_dim*__CM_TO_INCH))
    label_colors = []
    for label in labels: #, values in xy_values.items():
        x = xy_values[label]['x'] #[:max_x] if max_x else v['x']
        y = xy_values[label]['y'] #[:max_x] if max_x else v['y']
        #ax.plot(x, y, '-', color=next(line_color), label=label)
        v = ax.violinplot(y, x, showmeans=True, showextrema=True, showmedians=False,)
        label_colors.append(add_label(v,f"{label_prefix}{label}"))


    ax.set_title(title)
    ax.set_xlabel(x_lbl)
    ax.set_ylabel(y_lbl)


    if 'scale_x' in plot_params:
        ax.set_xscale(plot_params['scale_x'])
    if 'scale_y' in plot_params:
        ax.set_yscale(plot_params['scale_y'])

    scale = plot_params.get('scale', None)
    if scale == "percentage":
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(1.0))


    ax.set_xticks(np.arange(len(v_ticks)))
    ax.set_xticklabels(v_ticks)

    ax.legend(*zip(*label_colors), loc='upper center', ncol=lbl_ncol, bbox_to_anchor=lbl_pos,) #, loc='lower left')
    ax.grid(axis='y',which='both' )


    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)


    return filename
