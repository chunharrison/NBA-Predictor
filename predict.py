import os
import sys
from collections import defaultdict

from nba_api.stats.static import teams
from nba_api.stats.endpoints import leaguegamefinder, teaminfocommon, leaguestandings, teamyearbyyearstats

from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import f1_score, make_scorer, classification_report
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

import pandas as pd 
import numpy as np


    def predict(self):
        # TRAINING
        self.calculate_features(self.LAST_SEASON) # TRAINING features
        # FEATURE SELECTION
        # extract the features from the dataset to use with scikit-learn's RandomForestClassifier
        # by specifying the columns we wish to use and using the values parameter of a view of the dataframe
        # use the GridSearchCV function to test the result
        # 1
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
        # 2 
        encoding = LabelEncoder()
        encoding.fit(self.boxscore_df["Home Team Name"].values)
        home_teams = encoding.transform(self.boxscore_df["Home Team Name"].values)
        away_teams = encoding.transform(self.boxscore_df["Away Team Name"].values)
        X_teams = np.vstack([home_teams, away_teams]).T
        onehot = OneHotEncoder()
        X_teams = onehot.fit_transform(X_teams).todense()
        X_all = np.hstack([x_features_only, X_teams])

        # SAVE THE TRAINING DATA AND RESET boxscore_df
        training_data_df = self.boxscore_df
        self.boxscore_df = self.boxscore_df_pred

        # PREDICTING
        self.calculate_features(self.PREDICTING_SEASON)
        y_test = self.update_baseline() # baseline

        x_features_only_test = self.boxscore_df[features_list].values
        home_teams_test = encoding.transform(self.boxscore_df["Home Team Name"].values)
        away_teams_test = encoding.transform(self.boxscore_df["Away Team Name"].values)
        x_teams_test = np.vstack([home_teams_test, away_teams_test]).T
        x_teams_test = onehot.fit_transform(x_teams_test).todense()
        X_all_test = np.hstack([x_features_only_test, x_teams_test])


        # parameter_space = {
        #     "max_features": [2, 10, 50, 'auto'],
        #     "n_estimators": [50, 100, 200],
        #     "criterion": ["gini", "entropy"],
        #     "min_samples_leaf": [1, 2, 4, 6]
        # }
        parameter_space_tuned = {
            "max_features": 2,
            "n_estimators" 50,
            "criterion": "entropy",
            "min_samples_leaf": 6
        }
        clf = RandomForestClassifier(random_state=14)
        grid = GridSearchCV(clf, parameter_space_tuned, cv=5)
        grid.fit(X_all, y_true)
        y_pred = grid.predict(X_all_test)
        # print(classification_report(y_test, y_pred))
        # print(grid.best_estimator_)


        training_data_df.to_csv(os.path.join(self.DATA_DIR, "training.csv"))
        self.boxscore_df.to_csv(os.path.join(self.DATA_DIR, "actual.csv"))
        self.boxscore_df["Home Win"] = y_pred
        self.boxscore_df.to_csv(os.path.join(self.DATA_DIR, "predicted.csv"))


def main():
    c = NBADataToCSV()
    c.predict()

if __name__ == '__main__':
    main()
