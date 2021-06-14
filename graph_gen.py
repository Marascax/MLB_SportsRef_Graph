import matplotlib.pyplot as plt
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import seaborn as sns
import data_constants
import adjustText
import os
from matplotlib.patches import Ellipse, Polygon


def get_image(path):
    return OffsetImage(plt.imread(path), zoom=0.3)


plt.xkcd()


def generate(x, y, text=False):
    """
    Generated graph given pandas Series for x- & y-axis
    :param text: use text labels for points instead of images
    :param x: x-axis data
    :param y: y-axis data
    """
    fig, ax = plt.subplots(figsize=(15, 10))
    xmin, xmax = x.min(), x.max()
    ymin, ymax = y.min(), y.max()
    x0, y0, width, height = ax.get_tightbbox(fig.canvas.get_renderer()).bounds

    x_pixels_per_unit = width / (xmax - xmin)
    y_pixels_per_unit = height / (ymax - ymin)

    new_xmin = xmin - (75 / x_pixels_per_unit)
    new_xmax = xmax + (75 / x_pixels_per_unit)

    plt.xlim(new_xmin, new_xmax)

    new_ymin = ymin - (75 / y_pixels_per_unit)
    new_ymax = ymax + (75 / y_pixels_per_unit)

    plt.ylim(new_ymin, new_ymax)

    plt.vlines(x=(new_xmin + new_xmax) / 2, ymin=new_ymin, ymax=new_ymax, linestyles='dashed',
               colors=(0.0, 0.0, 0.0, 0.4))
    plt.hlines(y=(new_ymin + new_ymax) / 2, xmin=new_xmin, xmax=new_xmax, linestyles='dashed',
               colors=(0.0, 0.0, 0.0, 0.4))

    texts = []
    imgs = []
    for i, tm in enumerate(data_constants.teams):
        if text:
            # ax.annotate(tm, (x[i], y[i]))
            texts.append(ax.text(x[i], y[i], tm))
        else:
            imgs.append(
                ax.add_artist(
                    AnnotationBbox(
                        get_image(f'{os.path.dirname(os.path.abspath(__file__))}/plot_logos{os.path.sep}{tm}.png'),
                        (x[i], y[i]),
                        frameon=False
                   )
                )
            )

    if text:
        adjustText.adjust_text(texts)

    x_abbrev, y_abbrev = x.name, y.name
    x_verbose, y_verbose = data_constants.batting_to_verbose[x_abbrev], data_constants.batting_to_verbose[y_abbrev]

    # top left
    ax.text(xmin, ymax, f'High {y_abbrev}\nLow {x_abbrev}', ha='left', va='center', color=(0.0, 0.0, 0.0, 0.4))
    # bottom left
    ax.text(xmin, ymin, f'Low {y_abbrev}\nLow {x_abbrev}', ha='left', va='center', color=(0.0, 0.0, 0.0, 0.4))
    # top right
    ax.text(xmax, ymax, f'High {y_abbrev}\nHigh {x_abbrev}', ha='right', va='center', color=(0.0, 0.0, 0.0, 0.4))
    # bottom right
    ax.text(xmax, ymin, f'High {y_abbrev}\nHigh {x_abbrev}', ha='right', va='center', color=(0.0, 0.0, 0.0, 0.4))

    plt.xlabel(x_verbose, size=20)
    plt.ylabel(y_verbose, size=20)
    plt.title(f'{x_verbose} ({x_abbrev}) vs {y_verbose} ({y_abbrev})')
    # plt.tight_layout()

    plt.show()
    return

# import data_collect
# collected = data_collect.collect('BatAge', 'OPS+')
# generate(collected[0], collected[1])