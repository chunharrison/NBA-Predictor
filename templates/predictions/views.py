from flask import render_template, Blueprint

import pandas as pd
import json
from collections import defaultdict

# crate a blueprint for prediction page
predictions_blueprint = Blueprint('predictions', __name__)

TEAM_NAMES = [
    'Atlanta Hawks', 'Boston Celtics', 'Cleveland Cavaliers', 
    'New Orleans Pelicans', 'Chicago Bulls', 'Dallas Mavericks', 
    'Denver Nuggets', 'Golden State Warriors', 'Houston Rockets', 
    'Los Angeles Clippers', 'Los Angeles Lakers', 'Miami Heat', 
    'Milwaukee Bucks', 'Minnesota Timberwolves', 'Brooklyn Nets', 
    'New York Knicks', 'Orlando Magic', 'Indiana Pacers', 'Philadelphia 76ers', 
    'Phoenix Suns', 'Portland Trail Blazers', 'Sacramento Kings', 
    'San Antonio Spurs', 'Oklahoma City Thunder', 'Toronto Raptors', 
    'Utah Jazz', 'Memphis Grizzlies', 'Washington Wizards', 'Detroit Pistons', 
    'Charlotte Hornets'
]

@predictions_blueprint.route('/predictions')
def predictions():
    prediction_data = []
    teams_win_loss = defaultdict(lambda: defaultdict(int))
    df = pd.read_csv("./data/old/predicted.csv")
    for i in df.index:
        by_dates = {}
        date = df.at[i, "Date"]
        home = df.at[i, "Home Team Name"]
        away = df.at[i, "Away Team Name"]
        home_win = 1 if df.at[i, "Home Win"] == 1 else 0
        home_loss = 0 if df.at[i, "Home Win"] == 1 else 1
        away_win = 0 if df.at[i, "Home Win"] == 1 else 1
        away_loss = 1 if df.at[i, "Home Win"] == 1 else 0
        # winner = home if df.at[i, "Home Win"] == 1 else away

        teams_win_loss[home]["Wins"] += home_win
        teams_win_loss[home]["Losses"] += home_loss
        teams_win_loss[away]["Wins"] += away_win
        teams_win_loss[away]["Losses"] += away_loss

        home_pct = (float(teams_win_loss[home]["Wins"] * 100) / float(teams_win_loss[home]["Wins"]+teams_win_loss[home]["Losses"]))
        home_pct = round(home_pct, 2)
        by_dates[home] = home_pct
        away_pct = (float(teams_win_loss[away]["Wins"] * 100) / float(teams_win_loss[away]["Wins"]+teams_win_loss[away]["Losses"]))
        away_pct = round(away_pct, 2)
        by_dates[away] = away_pct
        by_dates["Date"] = date
        prediction_data.append(by_dates)

    prediction_data_combined = []
    date_tracker = ''
    combining_dict = {}
    for dic in prediction_data:
        current_date = dic["Date"]
        if date_tracker != current_date and date_tracker != '':
            prediction_data_combined.append(combining_dict)
            combining_dict = {}
        else:
            new_dict = {**combining_dict, **dic}
            combining_dict = new_dict
        date_tracker = current_date
    
    google_charts_data = []
    current_wr = {}
    for dic in prediction_data_combined:
        current_list = []
        current_list.append(dic["Date"])
        for team_name in TEAM_NAMES:
            default_value = current_wr.get(team_name, 0)
            current_list.append(dic.get(team_name, default_value))
        
        google_charts_data.append(current_list)

        hold_date = current_list.pop(0)
        current_wr = dict(zip(TEAM_NAMES, current_list))
        current_list.insert(0, hold_date)


    return json.dumps(google_charts_data)
