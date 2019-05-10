# NBA-Predictor
predicts the outcome of future NBA games



## Documentation:

- getData.py - updates data for training and predicting of the lastest NBA season
- predict.py - creates a model and predicts outcome of the latest NBA season



### Data Retreived From:

nba-api: https://github.com/swar/nba_api

basketball-reference.com: https://www.basketball-reference.com





# NOTES FOR FUTURE APPLICATIONS

######Winshares

Calculating offensive win shares to players.

Credit: Dean Oliver | http://www.basketballonpaper.com



Offsensive win shares

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



Defensive win shares

1. Calculate the Defensive Rating for each player. 
   - defensive rating for the season
2. Calculate marginal defense for each player.
   - (player minutes played / team minutes played) * (team defensive possessions) * (1.08 * (league points per possession) - ((Defensive Rating) / 100))
3. Calculate marginal points per win.
   - 0.32 * (league points per game) * ((team pace) / (league pace))
4. Credit Defensive Win Shares to the players.
   - (marginal defense) / (marginal points per win)

### 

Total win shares

offensive win shares + defensive win shares



