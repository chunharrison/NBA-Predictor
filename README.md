# NBA-Predictor
predicts the outcome of future NBA games



## Usage of NBAStats.py

- Command Line Arguments:
  - all - updates the csv file that holds game's entire data
  - seasons - updates all csv files that holds each season's game data
  - both - both





## Baseline

- home team wins games more frquently





##Win Shares

Calculating offensive win shares to players.

Credit: Dean Oliver | http://www.basketballonpaper.com

###offensive win shares

1. Calculate points producted for each player.
   - total points produced during the season
2. Calculate offensive possessions for each player.
   - total offensive possessions during the season
3. Calculate marginal offense for each player.
   - (points produced) - 0.92 * (league points per possession) * (offensive possessions)
   - may produce negative result for players
4. Calculate marginal points per win.
   - 0.32 * (league pointers per game) * ((team pace) / (league pace))
5. Credit offensive Win Shares to the players.
   - (marginal offense) / (marginal points per win)

###defensive win shares

1. Calculate the Defensive Rating for each player. 
   - defensive rating for the season
2. Calculate marginal defense for each player.
   - (player minutes played / team minutes played) * (team defensive possessions) * (1.08 * (league points per possession) - ((Defensive Rating) / 100))
3. Calculate marginal points per win.
   - 0.32 * (league points per game) * ((team pace) / (league pace))
4. Credit Defensive Win Shares to the players.
   - (marginal defense) / (marginal points per win)

### total win shares

offensive win shares + defensive win shares





## Decision Trees

- non-parametric supervised learning  method used for classification and regression
  - nonparametric statistics - statistical method in which the data is not required to fit a normal distribution. It uses data that is often ordinal, meaning it does not rely on numbers, but rather on a ranking or order of sorts.
  - 



