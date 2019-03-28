from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder

import pandas as pd 
import numpy as np

import os

from datetime import datetime

''' TEAM NAMES
[
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
'''

class NBADataToCSV():
    # list of all nba teams with their:
    # id, full_name, abbreviation, nickname, city, state, year_founded
    nba_teams = teams.get_teams()
    team_team_and_id = {}
    for team_data in nba_teams:
        team_team_and_id[team_data['full_name']] = team_data['id']
    season_list = [
        2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008,
        2007, 2006, 2005
    ]
    
    def get_game_data_all(self):
        for team_name, team_id in self.team_team_and_id.items():

            # query for games where the celtics were playing
            game_finder = leaguegamefinder.LeagueGameFinder(team_id_nullable=team_id)
            game_df_list = game_finder.get_data_frames()
            print(game_df_list)
            break

            # for index, game_df in enumerate(game_df_list):
            #     # formulate a proper file name
            #     game_csv_dir = './data_CSV/' + team_name
            #     if not os.path.exists(game_csv_dir):
            #         os.mkdir(game_csv_dir)
            #     game_csv_file = str(self.season_list[index]) + '.csv'
            #     game_csv_fullpath = os.path.join(game_csv_dir, game_csv_file)
            #     game_df.to_csv(game_csv_fullpath)


def main():
    c = NBADataToCSV()
    c.get_game_data_all()

if __name__ == '__main__':
    main()
