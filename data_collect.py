import pandas as pd
from sportsref.baseball import Season

pd.set_option('display.max_columns', None)
szn2021 = Season(2021)
bat21 = szn2021.batting_pages('standard').get_df('teams_standard_batting')
plot_df = bat21.query('Tm != "LgAvg"')
plot_df = plot_df.rename({'ops_plus': 'OPS+'}, axis=1)


def collect(x, y):
    """
    Get the data for each graph axis (from abbreviated name)
    :param x: stat category for x-axis
    :param y: stat category for y-axis
    :return: pandas Series for each stat
    """
    return plot_df[x], plot_df[y]


# print(collect('BatAge', 'OPS+'))
