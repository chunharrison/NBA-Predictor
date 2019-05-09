import os
import sys
import time
from collections import defaultdict

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, teaminfocommon, leaguestandings, teamyearbyyearstats

import pandas as pd 
import numpy as np

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import f1_score, make_scorer, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

start_time = time.time()

class NBADataToCSV():

    def __init__(self):
        # CONSTANTS
        self.SEASON_LIST = ["22017", "22016", "22015", "22014", "22013", "22012", "22011", "22010", "22009", "22008"]
        self.YEAR_LIST = ["2017", "2016", "2015", "2014", "2013", "2012", "2011", "2010", "2009", "2008"]
        self.RANKINGS_CSVS = ["2017.csv", "2016.csv", "2015.csv", "2014.csv", "2013.csv", "2012.csv", "2011.csv", "2010.csv", "2009.csv", "2008.csv", "2007.csv"]
        self.LAST_SEASON = "22008"
        self.DATA_DIR = './data'
        self.RANKINGS_DIR = "./data/rankings"

        # TESTING
        self.SEASON_TEST = "22018"

        # GAME DATAFRAME
        ## get full game df
        game_finder = leaguegamefinder.LeagueGameFinder(league_id_nullable='00')
        self.boxscore_df = game_finder.get_data_frames()[0]
        ## sort by seasons
        self.boxscore_df = self.boxscore_df[self.boxscore_df.SEASON_ID >= self.LAST_SEASON]
        self.boxscore_df = self.boxscore_df[self.boxscore_df.SEASON_ID.str[0] == '2']
        ## drop uneccessary columns
        noneed = self.boxscore_df.columns.values[10:]
        self.boxscore_df.drop(columns=noneed)
        self.boxscore_df.drop("MIN", axis=1)
        ## groupby unique game ids
        self.boxscore_df = self.boxscore_df.groupby('GAME_ID').agg(
            {
                "SEASON_ID": 'first',
                "TEAM_ABBREVIATION": ['first', 'last'],
                "TEAM_NAME": ['first', 'last'],
                "TEAM_ID": ['first', 'last'],
                "PTS": ['first', 'last'],
                "WL": 'first',
                "MATCHUP": 'first',
                "GAME_DATE": 'first'
            }
        )
        self.boxscore_df.columns = ["_".join(x) for x in self.boxscore_df.columns.ravel()]
        ## rename the columns
        df_columns = ["Season ID", "Home Team ABB", "Away Team ABB", "Home Team Name", "Away Team Name", "Home ID", "Away ID", "Home Points", "Away Points", "Home Win", "Match", "Date"]
        self.boxscore_df.columns = df_columns
        self.boxscore_df = self.boxscore_df.replace("LA Clippers", "Los Angeles Clippers")
        self.boxscore_df = self.boxscore_df.replace("New Jersey Nets", "Brooklyn Nets")
        self.boxscore_df = self.boxscore_df.replace("New Orleans Hornets", "New Orleans Pelicans")
        self.boxscore_df = self.boxscore_df.replace("Charlotte Bobcats", "Charlotte Hornets")
        
        # --------------------------------- TESTING ------------------------------------------------------------------------------------
        self.boxscore_df_pred = game_finder.get_data_frames()[0]
        self.boxscore_df_pred = self.boxscore_df_pred[self.boxscore_df_pred.SEASON_ID == self.SEASON_TEST] # TESTING
        self.boxscore_df_pred = self.boxscore_df_pred[self.boxscore_df_pred.SEASON_ID.str[0] == '2']
        ## drop uneccessary columns
        noneed = self.boxscore_df_pred.columns.values[10:]
        self.boxscore_df_pred.drop(columns=noneed)
        self.boxscore_df_pred.drop("MIN", axis=1)
        ## groupby unique game ids
        self.boxscore_df_pred = self.boxscore_df_pred.groupby('GAME_ID').agg(
            {
                "SEASON_ID": 'first',
                "TEAM_ABBREVIATION": ['first', 'last'],
                "TEAM_NAME": ['first', 'last'],
                "TEAM_ID": ['first', 'last'],
                "PTS": ['first', 'last'],
                "WL": 'first',
                "MATCHUP": 'first',
                "GAME_DATE": 'first'
            }
        )
        self.boxscore_df_pred.columns = ["_".join(x) for x in self.boxscore_df_pred.columns.ravel()]
        ## rename the columns
        df_columns = ["Season ID", "Home Team ABB", "Away Team ABB", "Home Team Name", "Away Team Name", "Home ID", "Away ID", "Home Points", "Away Points", "Home Win", "Match", "Date"]
        self.boxscore_df_pred.columns = df_columns
        self.boxscore_df_pred = self.boxscore_df_pred.replace("LA Clippers", "Los Angeles Clippers")
        self.boxscore_df_pred = self.boxscore_df_pred.replace("New Jersey Nets", "Brooklyn Nets")
        self.boxscore_df_pred = self.boxscore_df_pred.replace("New Orleans Hornets", "New Orleans Pelicans")
        self.boxscore_df_pred = self.boxscore_df_pred.replace("Charlotte Bobcats", "Charlotte Hornets")
        # --------------------------------- TESTING ------------------------------------------------------------------------------------

        # RANKINGS
        ## {year: {team: rank}}
        self.RANKS_BY_SEASONS = {}
        for rankings_csv in self.RANKINGS_CSVS:
            rankings_dir_full = os.path.join(self.RANKINGS_DIR, rankings_csv)
            rankings_df = pd.read_csv(rankings_dir_full, skiprows=1, index_col="Overall")
            rankings_df = rankings_df.replace("Seattle SuperSonics", 'Oklahoma City Thunder')
            rankings_df = rankings_df.replace("New Jersey Nets", "Brooklyn Nets")
            rankings_df = rankings_df.replace("New Orleans Hornets", "New Orleans Pelicans")
            rankings_df = rankings_df.replace("Charlotte Bobcats", "Charlotte Hornets")
            rankings_dict = pd.Series(rankings_df.Rk.values, index=rankings_df.Team).to_dict()
            self.RANKS_BY_SEASONS[rankings_csv[:4]] = rankings_dict
        
    def set_features(self):
        # FEATURES
        # 1 - Whether either of the visitor or home team won their last game.
        self.boxscore_df["Home Won Previous Match"] = False
        self.boxscore_df["Away Won Previous Match"] = False
        self.won_previous = defaultdict(int)

        # 2 - team win streaks
        self.boxscore_df["Home Win Streak"] = 0
        self.boxscore_df["Away Win Streak"] = 0
        self.win_streak = defaultdict(int)

        # 3 - The standing of the team
        self.boxscore_df["Home Team Higher Rank"] = 0

        # 4 - Which team won their last encounter (regardless of playing at home)
        self.boxscore_df["Home Team Won Last"] = 0
        self.last_match_winner = defaultdict(int)
        

    def organize_team_placements(self, df_index):
        # get organize the home and away teams
        if '@' in self.boxscore_df.at[df_index, "Match"]:
            # # team abbreviations swap
            # hold_team_abb = self.boxscore_df.at[df_index, "Home Team ABB"]
            # self.boxscore_df.at[df_index, "Home Team ABB"] = self.boxscore_df.at[df_index, "Away Team ABB"]
            # self.boxscore_df.at[df_index, "Away Team ABB"] = hold_team_abb

            # team names swap
            hold_team_name = self.boxscore_df.at[df_index, "Home Team Name"]
            self.boxscore_df.at[df_index, "Home Team Name"] = self.boxscore_df.at[df_index, "Away Team Name"]
            self.boxscore_df.at[df_index, "Away Team Name"] = hold_team_name

            # # team ids swap
            # hold_id = self.boxscore_df.at[df_index, "Home ID"]
            # self.boxscore_df.at[df_index, "Home ID"] = self.boxscore_df.at[df_index, "Away ID"]
            # self.boxscore_df.at[df_index, "Away ID"] = hold_id

            # team points swap
            hold_points = self.boxscore_df.at[df_index, "Home Points"]
            self.boxscore_df.at[df_index, "Home Points"] = self.boxscore_df.at[df_index, "Away Points"]
            self.boxscore_df.at[df_index, "Away Points"] = hold_points
    

    def baseline_home_win(self, df_index):
        home_win = 1 if self.boxscore_df.at[df_index, "Home Points"] > self.boxscore_df.at[df_index, "Away Points"] else 0
        self.boxscore_df.at[df_index, "Home Win"] = home_win

    def update_baseline(self):
        y_param = self.boxscore_df["Home Win"].values.astype('int')
        # print("HOME WINS {:2f}% OF MATCHES".format(np.mean(y_param)* 100))
        return y_param

    def feature_team_won_previous_match(self, df_index, home_team_name, away_team_name):
        self.boxscore_df.at[df_index, "Home Won Previous Match"] = self.won_previous[home_team_name]
        self.boxscore_df.at[df_index, "Away Won Previous Match"] = self.won_previous[away_team_name]
        self.won_previous[home_team_name] = self.boxscore_df.at[df_index, "Home Win"]
        self.won_previous[away_team_name] = not self.boxscore_df.at[df_index, "Home Win"]


    def feature_team_win_streaks(self, df_index, home_team_name, away_team_name):
        self.boxscore_df.at[df_index, "Home Win Streak"] = self.win_streak[home_team_name]
        self.boxscore_df.at[df_index, "Away Win Streak"] = self.win_streak[away_team_name]
        if self.boxscore_df.at[df_index, "Home Win"]:
            self.win_streak[home_team_name] += 1
            self.win_streak[away_team_name] = 0
        else:
            self.win_streak[home_team_name] = 0
            self.win_streak[away_team_name] += 1


    def feature_home_team_higher_rank(self, df_index, home_team_name, away_team_name, season_id):
        previous_year = str(int(season_id[-4:]) - 1)
        home_rank = self.RANKS_BY_SEASONS[previous_year][home_team_name]
        away_rank = self.RANKS_BY_SEASONS[previous_year][away_team_name]
        self.boxscore_df.at[df_index, "Home Team Higher Rank"] = int(home_rank < away_rank)

    def get_game_data(self):
        self.set_features()
        for i in self.boxscore_df.index:
            self.organize_team_placements(i)
            # teams
            home_team = self.boxscore_df.at[i, "Home Team Name"]
            away_team = self.boxscore_df.at[i, "Away Team Name"]
            # baseline
            self.baseline_home_win(i)
            # features
            self.feature_team_won_previous_match(i, home_team, away_team)
            self.feature_team_win_streaks(i, home_team, away_team)
            self.feature_home_team_higher_rank(i, home_team, away_team, self.boxscore_df.at[i, "Season ID"])
        #   4
            # sort for sonsistent ordering
            teams_sorted = tuple(sorted([home_team, away_team]))
            self.boxscore_df.at[i, "Home Team Won Last"] = 1 if self.last_match_winner[teams_sorted] == self.boxscore_df.at[i, "Home Team Name"] else 0
            winner = self.boxscore_df.at[i, "Home Team Name"] if self.boxscore_df.at[i, "Home Won Previous Match"] else self.boxscore_df.at[i, "Away Team Name"]
            self.last_match_winner[teams_sorted] = winner

    def predict(self):
        self.get_game_data() # TRAINING

        # FEATURE SELECTION
        # extract the features from the dataset to use with scikit-learn's RandomForestClassifier
        # by specifying the columns we wish to use and using the values parameter of a view of the dataframe
        # use the GridSearchCV function to test the result
        y_true = self.update_baseline()
        features_list = [
            "Home Won Previous Match",
            "Away Won Previous Match",
            "Home Win Streak",
            "Away Win Streak",
            "Home Team Higher Rank",
            "Home Team Won Last"
        ]
        x_features_only = self.boxscore_df[features_list].values

        encoding = LabelEncoder()
        encoding.fit(self.boxscore_df["Home Team Name"].values)

        home_teams = encoding.transform(self.boxscore_df["Home Team Name"].values)
        away_teams = encoding.transform(self.boxscore_df["Away Team Name"].values)
        x_teams = np.vstack([home_teams, away_teams]).T

        onehot = OneHotEncoder()
        x_teams = onehot.fit_transform(x_teams).todense()
        X_all = np.hstack([x_features_only, x_teams])

        # TESTING
        training_data_df = self.boxscore_df
        self.boxscore_df = self.boxscore_df_pred
        self.get_game_data() # TESTING
        y_test = self.update_baseline() # baseline

        x_features_only_test = self.boxscore_df[features_list].values
        home_teams_test = encoding.transform(self.boxscore_df["Home Team Name"].values)
        away_teams_test = encoding.transform(self.boxscore_df["Away Team Name"].values)
        x_teams_test = np.vstack([home_teams_test, away_teams_test]).T
        x_teams_test = onehot.fit_transform(x_teams_test).todense()
        X_all_test = np.hstack([x_features_only_test, x_teams_test])


        parameter_space = {
            "max_features": [2, 10, 50, 'auto'],
            "n_estimators": [50, 100, 200],
            "criterion": ["gini", "entropy"],
            "min_samples_leaf": [1, 2, 4, 6]
        }
        clf = RandomForestClassifier(random_state=14)
        grid = GridSearchCV(clf, parameter_space, cv=5)
        grid.fit(X_all, y_true)
        y_pred = grid.predict(X_all_test)
        print(classification_report(y_test, y_pred))


        training_data_df.to_csv(os.path.join(self.DATA_DIR, "training.csv"))
        self.boxscore_df.to_csv(os.path.join(self.DATA_DIR, "actual.csv"))
        self.boxscore_df["Home Wins"] = y_pred
        self.boxscore_df.to_csv(os.path.join(self.DATA_DIR, "predicted.csv"))



def main():
    c = NBADataToCSV()
    c.get_game_data()
    c.predict()

if __name__ == '__main__':
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
