# team abbreviation list
teams = ['ARI', 'ATL', 'BAL', 'BOS', 'CHC', 'CHW', 'CIN', 'CLE', 'COL', 'DET', 'HOU', 'KCR', 'LAA', 'LAD', 'MIA',
         'MIL', 'MIN', 'NYM', 'NYY', 'OAK', 'PHI', 'PIT', 'SDP', 'SEA', 'SFG', 'STL', 'TBR', 'TEX', 'TOR', 'WSN']

# batting stats verbose names to abbreviations
batting_from_verbose = {
    'Number of Batters': '#Bat',
    'Average Age of Batters': 'BatAge',
    'Runs Per Game': 'R/G',
    'Games': 'G',
    'Plate Appearances': 'PA',
    'At Bats': 'AB',
    'Runs': 'R',
    'Hits': 'H',
    'Doubles': '2B',
    'Triples': '3B',
    'Home Runs': 'HR',
    'Runs Batted In': 'RBI',
    'Stolen Bases': 'SB',
    'Caught Stealing': 'CS',
    'Walks': 'BB',
    'Strikeouts': 'SO',
    'Batting Average': 'BA',
    'On-base Percentage': 'OBP',
    'Slugging': 'SLG',
    'On-base Plus Slugging': 'OPS+',
    'Total Bases': 'TB',
    'Grounded Into Double Plays': 'GDP',
    'Hit By Pitches': 'HBP',
    'Shutouts': 'SH',
    'Sacrifice Flies': 'SF',
    'Intentional Walks': 'IBB',
    'Left On-base': 'LOB'
}

# batting stats abbreviations to verbose names
# reverse pairs of dict with verbose name keys
batting_to_verbose = {v: k for (k, v) in batting_from_verbose.items()}