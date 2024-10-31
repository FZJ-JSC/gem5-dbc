from pandas import DataFrame

import matplotlib.pyplot as plt
import numpy as np

import math
import re

__epsilon = 1e-8
__cm_to_inch = 1/2.54

def normalize_pdf(pdf: np.ndarray):
    res = pdf / pdf.sum()
    max_idx = np.argmax(res < __epsilon)
    res = res[:max_idx]
    return res

def calculate_mean_std(pdf: np.ndarray, x: np.ndarray):
    mu = np.dot(pdf,x)
    dx2 = (x - mu)*(x-mu)
    std = math.sqrt(np.dot(pdf,dx2))

    return (mu,std)


def plot_histogram(filename: str, xy_values: dict, plot_params: dict, dpi=600):
    
    x_lbl = plot_params['x_label']
    y_lbl = plot_params['y_label']
    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)

    bar_width = plot_params.get('bar_width', 0.12)
    label_fmt = plot_params.get('label_fmt', "{}")

    lbl_pos  = plot_params.get('lbl_pos', (0.5, 1.2))
    lbl_ncol = plot_params.get('lbl_ncol', 3)

    labels    = sorted(xy_values.keys())
    nbars     = len(labels)
    bar_delta = [bar_width*(x-(nbars-1)/2) for x in np.arange(nbars)]
    bar_color = iter([plt.get_cmap("tab20")(i) for i in range(20)])

    fig, ax = plt.subplots(figsize=(x_dim*__cm_to_inch, y_dim*__cm_to_inch))
    bars = []
    for i, l in enumerate(labels):
        x = xy_values[l]['x']
        y = xy_values[l]['y']
        plot_x = x - bar_delta[i]
        plot_y = y
        mu, std = calculate_mean_std(y, x)
        label = label_fmt.format(l) + r" $\;\overline{{H}}={:.2f} \pm {:.2f}$".format(mu,std)
        bars.append(ax.bar(plot_x, plot_y, bar_width, color=next(bar_color), label=label ))
    
    ax.set_xlabel(x_lbl)
    ax.set_ylabel(y_lbl)

    ax.legend(loc='upper center',  ncol=lbl_ncol, bbox_to_anchor=lbl_pos,)

    ax.grid(axis='y')

    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)

    return