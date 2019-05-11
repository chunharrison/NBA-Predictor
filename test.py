from flask import Flask, render_template

import pandas as pd
import json
from collections import defaultdict

app = Flask(__name__)

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

by_dates = {}

teams_pct = {key:0 for key in TEAM_NAMES}
teams_win_loss = defaultdict(lambda: defaultdict(int))
df = pd.read_csv("./data/old/predicted")
for i in df.index:
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

    home_pct = home_win / (home_win+home_loss)
    teams_pct[home] = home_pct
    away_pct = away_win / (away_win+away_loss)
    teams_pct[away] = away_pct
    home_pct["Date"] = date
    
    by_dates[date] = teams_pct

chart_data = json.dumps(by_dates, indent=2)
data = {'chart_data': chart_data}
print(data)
return render_template("index.html", data=data)