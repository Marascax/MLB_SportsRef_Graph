import pandas as pd
from sportsref.baseball import Season
from datetime import date

pd.set_option('display.max_columns', None)
plot_df = None
collect_date = None


def collect_data():
    szn2021 = Season(2021)

    # get batting, pitching, and baserunning dataframes while dropping any known duplicate stats
    bat_df = szn2021.batting_pages('standard').get_df('teams_standard_batting').drop(['G'], axis=1)
    pitch_df = szn2021.pitching_pages('standard').get_df('teams_standard_pitching').drop(['G'], axis=1)
    baserun_df = szn2021.batting_pages('baserunning').get_df('teams_baserunning_batting').drop(['R/G', 'SB', 'CS'], axis=1)
    bp_df = bat_df.merge(pitch_df, on='Tm')

    # rename stats with identical abbreviations to represent whether they are a hitting or pitching stat more clearly
    bp_df = bp_df.rename({'ops_plus': 'OPS+', 'GDP': 'GIDP', 'R_x': 'R_h', 'H_x': 'H_h', 'HR_x': 'HR_h', 'BB_x': 'BB_h',
                          'IBB_x': 'IBB_h', 'SO_x': 'SO_h', 'HBP_x': 'HBP_h', 'LOB_x': 'LOB_h', 'R_y': 'R_p', 'H_y': 'H_p',
                          'HR_y': 'HR_p', 'BB_y': 'BB_p', 'IBB_y': 'IBB_p', 'SO_y': 'SO_p', 'HBP_y': 'HBP_p',
                          'LOB_y': 'LOB_p'}, axis=1)
    # print(bp_df.head())
    df = bp_df.merge(baserun_df, on='Tm')
    filtered_df = df.query('Tm != "League Average"')
    filtered_df["XBT%"] = filtered_df["XBT%"].str.replace('%','').astype(int) / 100
    return filtered_df


def get_data(x, y):
    """
    Get the data for each graph axis (from abbreviated name)
    :param x: stat category for x-axis
    :param y: stat category for y-axis
    :return: pandas Series for each stat
    """
    global plot_df, collect_date
    # check to see if data hasn't already been collected today in the current session
    if plot_df is None or date.today() > collect_date:
        plot_df = collect_data()
        collect_date = date.today()

    return plot_df[x], plot_df[y]
