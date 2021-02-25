from sportsipy.nhl.teams import Teams
from sportsipy.nhl.roster import Player
from sportsipy.nhl.roster import Roster
import pandas as pd
from datetime import datetime

startTime = datetime.now()

# Function to get player info from Player class object.
def get_player_df(player):
    # helper function to get year for each row and denote
    # rows that contain career totals.
    def get_year(ix):
        if ix[0] == "Career":
            return "Career"
        elif ix[0] == "1999-00":
            return "2000"
        else:
            return ix[0][0:2] + ix[0][-2:]
    
    # get player df and add some extra info
    player_df = player.dataframe # establish dataframe
    player_df['player_id'] = player.player_id # player_id field is populated with player_id
    player_df['name'] = player.name # name field gets player name
    player_df['year'] = [get_year(ix) for ix in player_df.index] # year field gets the year of each season pulled
    player_df.set_index('player_id', drop = True, inplace = True) # this was 'id' before but i dont want id
    
    return player_df

# initialize a list of players that we have pulled data for
players_collected = []
season_df_init = 0
career_df_init = 0
season_df = 0
career_df = 0
years = ['2020']
# iterate through years.
for year in years:
    print('\n' + str(year))
        
    # iterate through all teams in that year.
    for team in Teams(year = str(year)).dataframes.index:
        print('\n' + team + '\n')
        
        # iterate through every player on a team roster.
        for player_id in Roster(team, year = year,
                         slim = True).players.keys():
            
            # only pull player info if that player hasn't
            # been pulled already.
            if player_id not in players_collected:
                try:
                    player = Player(player_id)
                    player_info = get_player_df(player)
                    player_seasons = player_info[
                                     player_info['year'] != "Career"]
                    player_career = player_info[
                                    player_info['year'] == "Career"]
                except:
                    pass
                # create season_df if not initialized
                if not season_df_init:
                    try:
                        season_df = player_seasons
                        season_df_init = 1
                    except:
                        pass
                # else concatenate to season_df
                else:
                    try:
                        season_df = pd.concat([season_df,
                                       player_seasons], axis = 0)
                    except:
                        pass
                if not career_df_init:
                    try:
                        career_df = player_career
                        career_df_init = 1
                    except:
                        pass
                # else concatenate to career_df
                else:
                    try:
                        career_df = pd.concat([career_df,
                                       player_career], axis = 0)
                    except:
                        pass

                # add player to players_collected
                players_collected.append(player_id)
                print(player.name)

print(datetime.now()-startTime)