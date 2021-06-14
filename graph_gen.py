import matplotlib.pyplot as plt
import seaborn as sns
import data_constants
import adjustText
from matplotlib.patches import Ellipse, Polygon

plt.xkcd()


def generate(x, y):
    """
    Generated graph given pandas Series for x- & y-axis
    :param x: x-axis data
    :param y: y-axis data
    """
    fig, ax = plt.subplots(figsize=(15, 10))
    sns.regplot(x, y)
    texts = []
    for i, tm in enumerate(data_constants.teams):
        # ax.annotate(tm, (x[i], y[i]))
        texts.append(ax.text(x[i], y[i], tm))
    adjustText.adjust_text(texts)

    plt.xlim((x.min(), x.max()))

    x_abbrev, y_abbrev = x.name, y.name
    x_verbose, y_verbose = data_constants.batting_to_verbose[x_abbrev], data_constants.batting_to_verbose[y_abbrev]
    plt.xlabel(x_verbose, size=20)
    plt.ylabel(y_verbose, size=20)
    plt.title('{} ({}) vs {} ({})'.format(x_verbose, x_abbrev, y_verbose, y_abbrev))
    plt.tight_layout()
    plt.show()
    return

# import data_collect
# collected = data_collect.collect('BatAge', 'OPS+')
# generate(collected[0], collected[1])