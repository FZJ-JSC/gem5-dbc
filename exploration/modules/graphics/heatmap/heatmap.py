import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

__cm_to_inch = 1/2.54

# matplotlib code taken from 
# https://matplotlib.org/3.1.1/gallery/images_contours_and_fields/image_annotated_heatmap.html

def noc_heatmap(rdata, row_labels=[], col_labels=[], ax=None, cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()
        
    data = rdata #np.flip(rdata,0)
    nrows, ncols = np.shape(data)
    
    # Plot the heatmap
    im = ax.imshow(data, **kwargs)
    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")
    
    ax.set_xticks(np.arange(ncols))
    ax.set_yticks(np.arange(nrows))

    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(ncols+1)-.5, minor=True)
    ax.set_yticks(np.arange(nrows+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


def annotate_heatmap(im, data=None, tile_labels=None, textcolors=["black", "white"],
                     threshold=None, fmtstr="{label}\n{value:.2E}",**textkw):

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()
    
    nrows, ncols = np.shape(data)
    #if labels is None:
    #    labels = np.flip(np.reshape([f"R{c}" for c in range(nrows*ncols)], ( nrows,ncols)),0)

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center", verticalalignment="center")
    kw.update(textkw)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(nrows):
        for j in range(ncols):
            kw.update(color=textcolors[int(im.norm(data[i, j]) > threshold)])
            if(tile_labels[i,j] != None):
                text = im.axes.text(j, i, fmtstr.format(label=tile_labels[i, j],value=data[i, j]), **kw)
                texts.append(text)

    return texts


def add_core_rectangles(ax):
    ax.add_patch(Rectangle((5.5, 1.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    ax.add_patch(Rectangle((3.5, 1.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    
    ax.add_patch(Rectangle((5.5, 3.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    ax.add_patch(Rectangle((3.5, 3.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    ax.add_patch(Rectangle((1.5, 3.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    
    ax.add_patch(Rectangle((5.5, 5.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    ax.add_patch(Rectangle((3.5, 5.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    ax.add_patch(Rectangle((1.5, 5.5), 2, 2, fill=False, edgecolor='black', lw=3, zorder=100))
    
    return ax

# def write_heatmap2(data, tile_labels, title, desc, filename, fmtstr="{label}\n{value:.2E}", row_labels=[], col_labels=[], dpi=600):
#     cm_to_inch = 1/2.54

#     nrows, ncols = np.shape(data)

#     fig, ax = plt.subplots(figsize=(12*cm_to_inch, 10*cm_to_inch))

#     fontsize = 5.0 if (nrows > 4) else 11.0
#     fontweight = 'normal' #'light' if (nrows > 4) else 'normal'

#     im, cbar = noc_heatmap(data, ax=ax, cmap="Blues", row_labels=row_labels, col_labels=col_labels, cbarlabel=desc)
#     texts = annotate_heatmap(im, tile_labels=tile_labels, fmtstr=fmtstr, fontsize=fontsize, fontweight=fontweight )
#     ax.set_title(title)
    
#     if (nrows > 4):
#         add_core_rectangles(ax)

#     fig.tight_layout()

#     print(f"Writing image to {filename}")
#     plt.savefig(filename, dpi=dpi)
    
#     plt.close(fig)


def label_heatmap(im, tile_labels: np.array, plot_params: dict):

    tile_fmt  = plot_params.get("tile_fmt","{label}\n{value:.2E}")
    txt_color = plot_params.get("txt_color",["black", "white"])

    data = im.get_array()

    nrows, ncols = np.shape(data)

    threshold = im.norm(data.max())/2.

    kw = dict(
        horizontalalignment="center",
        verticalalignment="center",
        )

    texts = []
    for i in range(nrows):
        for j in range(ncols):
            kw.update(color=txt_color[int(im.norm(data[i, j]) > threshold)])
            if(tile_labels[i,j] != None):
                text = im.axes.text(
                    j, i,
                    tile_fmt.format(label=tile_labels[i, j],value=data[i, j]).replace(r'%', r'\%'),
                    **kw)
                texts.append(text)

    return texts


def write_heatmap(filename: str, xy_values: dict, plot_params: dict, dpi=600):

    x_dim = plot_params.get('x_dim', 24)
    y_dim = plot_params.get('y_dim', 12)
    y_label = plot_params.get('y_label','')
    x_labels = plot_params.get('x_labels', [])
    y_labels = plot_params.get('y_labels', [])
    x_ticks = plot_params.get('x_ticks', [])
    y_ticks = plot_params.get('y_ticks', [])

    title = plot_params.get('title','')

    values = xy_values["values"]
    labels = xy_values["labels"]

    fig, ax = plt.subplots(figsize=(x_dim*__cm_to_inch, y_dim*__cm_to_inch))

    # Plot the heatmap
    im = ax.imshow(values, cmap="Blues",)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax)
    cbar.ax.set_ylabel(y_label, rotation=-90, va="bottom")

    ax.set_xticks(x_ticks)
    ax.set_yticks(y_ticks)
    ax.set_xticklabels(x_labels)
    ax.set_yticklabels(y_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False, labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right", rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    label_heatmap(im, labels, plot_params)
    ax.set_title(title)

    fig.tight_layout()

    plt.savefig(filename, dpi = dpi)

    plt.close(fig)

    return
