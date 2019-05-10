from nba_api.stats.endpoints import leaguegamefinder

    # def update_baseline(self):
    #     y_param = self.boxscore_df["Home Win"].values.astype('int')
    #     # print("HOME WINS {:2f}% OF MATCHES".format(np.mean(y_param)* 100))
    #     return y_param

class DataToCSV():
    # CONSTANTS
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
    # RANKINGS_CSVS = ["2017.csv", "2016.csv", "2015.csv", "2014.csv", "2013.csv", "2012.csv"]
    LAST_SEASON = "22008"
    LATEST_SEASON = "22017"
    PREDICTING_SEASON = "22018"
    TRAINING_CSV = './data/training.csv'
    PREDICTING_CSV = './data/outcome.csv'
    RANKINGS_DIR = "./data/rankings"

    # GAME DATAFRAME
    ## get full game df
    boxscore_df = leaguegamefinder.LeagueGameFinder(league_id_nullable='00').get_data_frames()[0]


    ################################## Modifying the raw data retreived from nba_api ##################################
    # LeagueGameFinder gives every single nba games on file.
    # trim_df_by_seasons removes any unwanted seasons from the dataframe.
    def trim_df_by_seasons(self, latest_season, last_season):
        self.boxscore_df = self.boxscore_df[self.boxscore_df.SEASON_ID >= last_season]
        self.boxscore_df = self.boxscore_df[self.boxscore_df.SEASON_ID <= latest_season]
        self.boxscore_df = self.boxscore_df[self.boxscore_df.SEASON_ID.str[0] == '2']

    # LeagueGameFinder contains many unnecessary data that we do not need as our features.
    # remove_df_unnecessary_columns removes any unwanted data(columns) from the dataframe.
    def remove_df_unnecessary_columns(self):
        noneed = self.boxscore_df.columns.values[10:]
        self.boxscore_df.drop(columns=noneed)
        self.boxscore_df.drop("MIN", axis=1)
        self.boxscore_df.drop("TEAM_ABBREVIATION", axis=1)
        self.boxscore_df.drop("TEAM_ID", axis=1)

    # LeagueGameFinder contains duplicate rows for a game for each teams.
    # group_df_by_game_id_then_rename_columns groups the data frame by unique game ids and then fix the column names
    def group_df_by_game_id_then_rename_columns(self):
        self.boxscore_df = self.boxscore_df.groupby('GAME_ID').agg(
            {
                "SEASON_ID": 'first',
                "TEAM_NAME": ['first', 'last'],
                "PTS": ['first', 'last'],
                "WL": 'first',
                "MATCHUP": 'first',
                "GAME_DATE": 'first'
            }
        )
        # fixing column names
        self.boxscore_df.columns = ["_".join(x) for x in self.boxscore_df.columns.ravel()]
        df_columns = ["Season ID", "Home Team Name", "Away Team Name", "Home Points", "Away Points", "Home Win", "Match", "Date"]
        self.boxscore_df.columns = df_columns

    # Some NBA teams had their names changed over the years
    # update_old_team_names changes the old team names in the dataframe to latest
    def update_old_team_names(self):
        self.boxscore_df = self.boxscore_df.replace("LA Clippers", "Los Angeles Clippers")
        self.boxscore_df = self.boxscore_df.replace("New Jersey Nets", "Brooklyn Nets")
        self.boxscore_df = self.boxscore_df.replace("New Orleans Hornets", "New Orleans Pelicans")
        self.boxscore_df = self.boxscore_df.replace("Charlotte Bobcats", "Charlotte Hornets")
    
    # from group_df_by_game_id_then_rename_columns, self.boxscore_df has a scrambled orderings of home and away teams
    # relocate_teams_points reorders them in a correct columns by looking at the MATCH column value or each row
    def relocate_teams_points(self):
        for i in self.boxscore_df.index:
            if '@' in self.boxscore_df.at[i, "Match"]:
                # team names swap
                hold_team_name = self.boxscore_df.at[i, "Home Team Name"]
                self.boxscore_df.at[i, "Home Team Name"] = self.boxscore_df.at[i, "Away Team Name"]
                self.boxscore_df.at[i, "Away Team Name"] = hold_team_name

                # team points swap
                hold_points = self.boxscore_df.at[i, "Home Points"]
                self.boxscore_df.at[i, "Home Points"] = self.boxscore_df.at[i, "Away Points"]
                self.boxscore_df.at[i, "Away Points"] = hold_points

    def modify_nba_api_df(self, latest_season, last_season):
        self.trim_df_by_seasons(latest_season, last_season)
        self.remove_df_unnecessary_columns()
        self.group_df_by_game_id_then_rename_columns()
        self.update_old_team_names()
        self.relocate_teams_points()
        self.boxscore_df.drop("Match", axis=1) # we can remove the Match column now


def main():
    training_data = DataToCSV()
    training_data.modify_nba_api_df(training_data.LATEST_SEASON, training_data.LAST_SEASON)
    training_data.boxscore_df.to_csv(training_data.TRAINING_CSV)

    predicting_data = DataToCSV()
    predicting_data.modify_nba_api_df(predicting_data.PREDICTING_SEASON, predicting_data.PREDICTING_SEASON)
    predicting_data.boxscore_df.to_csv(predicting_data.PREDICTING_CSV)

if __name__ == '__main__':
    main()
