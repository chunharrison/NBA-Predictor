import pandas as pd
import os


class SetFeatures(): 
    # RANKINGS
    ## from https://www.basketball-reference.com, TODO: automate getting the latest rankings
    ## {year: {team: rank}}
    RANKINGS_CSVS = ["2017.csv", "2016.csv", "2015.csv", "2014.csv", "2013.csv", "2012.csv", "2011.csv", "2010.csv", "2009.csv", "2008.csv", "2007.csv"]
    RANKINGS_DIR = "./data/rankings"
    RANKS_BY_SEASONS = {}
    for rankings_csv in self.RANKINGS_CSVS:
        rankings_dir_full = os.path.join(self.RANKINGS_DIR, rankings_csv)
        rankings_df = pd.read_csv(rankings_dir_full, skiprows=1, index_col="Overall")
        rankings_df = rankings_df.replace("Seattle SuperSonics", 'Oklahoma City Thunder')
        rankings_df = rankings_df.replace("New Jersey Nets", "Brooklyn Nets")
        rankings_df = rankings_df.replace("New Orleans Hornets", "New Orleans Pelicans")
        rankings_df = rankings_df.replace("Charlotte Bobcats", "Charlotte Hornets")
        rankings_dict = pd.Series(rankings_df.Rk.values, index=rankings_df.Team).to_dict()
        self.RANKS_BY_SEASONS[rankings_csv[:4]] = rankings_dict
    
    def __init__(self, csv_file_name):
        self.boxscore_df = pd.read_csv(csv_file_name)

    # update the base line
    def baseline_home_win(self, df_index):
        home_win = 1 if self.boxscore_df.at[df_index, "Home Points"] > self.boxscore_df.at[df_index, "Away Points"] else 0
        self.boxscore_df.at[df_index, "Home Win"] = home_win

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

    def calc_feature_team_won_previous_match(self, df_index, home_team_name, away_team_name):
        self.boxscore_df.at[df_index, "Home Won Previous Match"] = self.won_previous[home_team_name]
        self.boxscore_df.at[df_index, "Away Won Previous Match"] = self.won_previous[away_team_name]
        self.won_previous[home_team_name] = self.boxscore_df.at[df_index, "Home Win"]
        self.won_previous[away_team_name] = not self.boxscore_df.at[df_index, "Home Win"]

    def calc_feature_team_win_streaks(self, df_index, home_team_name, away_team_name):
        self.boxscore_df.at[df_index, "Home Win Streak"] = self.win_streak[home_team_name]
        self.boxscore_df.at[df_index, "Away Win Streak"] = self.win_streak[away_team_name]
        if self.boxscore_df.at[df_index, "Home Win"]:
            self.win_streak[home_team_name] += 1
            self.win_streak[away_team_name] = 0
        else:
            self.win_streak[home_team_name] = 0
            self.win_streak[away_team_name] += 1

    def calc_feature_home_team_higher_rank(self, df_index, home_team_name, away_team_name, season_id):
        previous_year = str(int(season_id[-4:]) - 1)
        home_rank = self.RANKS_BY_SEASONS[previous_year][home_team_name]
        away_rank = self.RANKS_BY_SEASONS[previous_year][away_team_name]
        self.boxscore_df.at[df_index, "Home Team Higher Rank"] = int(home_rank < away_rank)

    def calc_feature_team_win_previous_match(self, df_index, home_team_name, away_team_name):
        # sort for sonsistent ordering
        teams_sorted = tuple(sorted([home_team_name, away_team_name]))
        self.boxscore_df.at[df_index, "Home Team Won Last"] = 1 if self.last_match_winner[teams_sorted] == self.boxscore_df.at[df_index, "Home Team Name"] else 0
        winner = self.boxscore_df.at[df_index, "Home Team Name"] if self.boxscore_df.at[df_index, "Home Won Previous Match"] else self.boxscore_df.at[df_index, "Away Team Name"]
        self.last_match_winner[teams_sorted] = winner



    def calculate_features(self):
        self.set_features()
        for i in self.boxscore_df.index:
            self.organize_df(i)
            # teams
            home_team = self.boxscore_df.at[i, "Home Team Name"]
            away_team = self.boxscore_df.at[i, "Away Team Name"]
            # baseline
            self.baseline_home_win(i)
            # features
            self.calc_feature_team_won_previous_match(i, home_team, away_team)
            self.calc_feature_team_win_streaks(i, home_team, away_team)
            self.calc_feature_home_team_higher_rank(i, home_team, away_team, self.boxscore_df.at[i, "Season ID"])
            self.calc_feature_team_win_previous_match(i, home_team, away_team)