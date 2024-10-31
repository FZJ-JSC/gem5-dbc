# Function definition
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mtick
import numpy as np

from utils.config import hatches, palettes 

def roofline_limits(x, p_bandwidth, p_flops):
    return min(x * p_bandwidth, p_flops)

def get_closest_matching_palette(hue_length, palettes): 
    for palette in palettes: 
        if hue_length <= len(palette): 
            return palette[:hue_length]
    return sns.color_palette("colorblind")

def scatterplot(df: pd.DataFrame, x: str, y: str, hue: str = None, style: str = None, save_path=None, xlabel=None, ylabel=None, title=None, xlim=None, s=100, ylim=None, use_pct_x=False, use_pct_y=False, hue_order=None, style_order=None, ax=None): 

    # default palette is colorblind
    palette = sns.color_palette("colorblind")


    if ax is None: 
        _, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=300)

    # get the appropriate palette
    if hue is not None: 
        hue_length = len(df[hue].unique())
        palette = get_closest_matching_palette(hue_length, palettes)

    ax = sns.scatterplot(
            data=df, 
            x=x, 
            y=y, 
            ax=ax, 
            hue=hue,
            style=style, 
            hue_order=hue_order, 
            style_order=style_order,
            palette=palette, 
            s=s
            )


    if xlim is not None: 
        ax.set_xlim(xlim)

    if ylim is not None: 
        ax.set_ylim(ylim)     

    if title is not None: 
        ax.set_title(algo, fontsize=15)

    if xlabel is not None: 
        ax.set_xlabel(xlabel, fontsize=14)
    else: 
        ax.set_xlabel(ax.get_xlabel(), fontsize=14)

    if ylabel is not None: 
        ax.set_ylabel(xlabel, fontsize=14)
    else: 
        ax.set_ylabel(ax.get_ylabel(), fontsize=14)


    fmt = '%.f%%' 
    xticks = mtick.FormatStrFormatter(fmt)

    if use_pct_x: 
        ax.xaxis.set_major_formatter(xticks)

    if use_pct_y: 
        ax.yaxis.set_major_formatter(xticks)


    ax.tick_params(axis='both', which='major', labelsize=15)
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels,  fontsize=15)

    if save_path is not None: 
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0.4)

    return ax


def roofline(df: pd.DataFrame, x, y, peak_bw, peak_flops, hue: str = None, style: str = None,  save_path=None, xlabel=None, ylabel=None, title=None, xlim=None, s=100, hue_order = None, style_order = None, ax = None):

    if ax is None: 
        _, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=300)


    palette = sns.color_palette("colorblind")

    df_to_plot = df.copy()
    if hue is not None: 
        df_to_plot = df_to_plot.groupby([hue]).mean().reset_index()
        hue_length = len(df_to_plot[hue].unique())
        palette = get_closest_matching_palette(hue_length, palettes)


    ## Roofline
    roofline_granularity = 0.01
    intensity = np.linspace(0, 20, int(20 / roofline_granularity))

    roofline = [roofline_limits(i, peak_bw, peak_flops) for i in intensity]

    sns.lineplot(x=intensity, y=roofline, ax=ax)
    sns.scatterplot(
            data=df_to_plot,
            x=x,
            y=y,
            hue=hue,
            style=style,
            ax=ax,
            hue_order=hue_order,
            style_order=style_order,
            palette=palette,
            s=s
            )

    ax.set(xscale="log", yscale="log")

    if xlabel is not None: 
        ax.set_xlabel(xlabel, fontsize=14)
    else: 
        ax.set_xlabel(ax.get_xlabel(), fontsize=14)


    if ylabel is not None: 
        ax.set_ylabel(ylabel, fontsize=14)
    else: 
        ax.set_ylabel(ax.get_ylabel(), fontsize=14)

    if save_path is not None: 
        plt.savefig(save_path, bbox_inches='tight', pad_inches=0.4)


    return ax

def cat_barplot(df: pd.DataFrame, x, y, hue: str = None, save_path=None, xlabel=None, ylabel=None, title=None, hue_order = None, use_pct_y = False, vline_at: int = -1, ci=95, ax = None):

    palette = sns.color_palette("colorblind")

    if ax is None: 
        _, ax = plt.subplots(1, 1, figsize=(10, 10), dpi=300)

    my_hatches = ["/"]

    if hue is not None: 
        hue_length = len(df[hue].unique())
        palette = get_closest_matching_palette(hue_length, palettes)
        my_hatches = hatches[:hue_length]


    ax = sns.barplot(data=df, x=x, y=y, hue=hue, ax=ax, palette=palette, ci=ci)
    max_y = df[y].max()

    if ylabel is not None: 
        ax.set_ylabel(ylabel, fontsize=14)
    else: 
        ax.set_ylabel(ax.get_ylabel(), fontsize=14)


    if xlabel is not None: 
        ax.set_xlabel(xlabel, fontsize=14)
    else: 
        ax.set_xlabel(ax.get_xlabel(), fontsize=14)

    if use_pct_y: 
        ax.yaxis.set_major_formatter(lambda x, _: f"{x:.0f}%")

    for j, bar in enumerate(ax.patches): 
        bar.set_hatch(my_hatches[j // len(df[x].unique())])
        bar.set_edgecolor("#121212")


    for i, p in enumerate(ax.patches): 
        if p.get_height() < 0.8 * max_y: 
            ax.text(p.get_x() + p.get_width() / 2, p.get_height() + max_y * 0.05, f"{p.get_height():.2f}", ha="center", va="bottom", rotation=0, fontsize=9)
        else: 
            ax.text(p.get_x() + p.get_width() / 2, p.get_height() + max_y * 0.05, f"{p.get_height():.2f}", ha="center", va="bottom", rotation=0, fontsize=9)

    if vline_at >= 0: 
        ax.axvline(x=vline_at, ls="--", color="#a0a0a0")


    ax.set_ylim((0, 1.5 * max_y))

    if save_path is not None: 
        plt.savefig(save_path, bbox_inches="tight", pad_inches=0)        

    return ax

