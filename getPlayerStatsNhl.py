from sportsipy.nhl.teams import Teams
from sportsipy.nhl.roster import Player
from sportsipy.nhl.roster import Roster
import pandas as pd
from datetime import datetime
from nhlCols import cols
import os
import gspread
from nhlSecrets import nhlPlayerFolderId, playerDashboardURL

# TODO Add gspread functionality.

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
    # player_id field is populated with player_id
    player_df['player_id'] = player.player_id 
    player_df['name'] = player.name # name field gets player name
    # year field gets the year of each season pulled
    player_df['year'] = [get_year(ix) for ix in player_df.index] 
    # this was 'id' before but i dont want id
    player_df.set_index('player_id', drop = True, inplace = True)
    
    return player_df

# initialize a list of players that we have pulled data for
players_collected = []
season_df_init = 0
career_df_init = 0
season_df = 0
career_df = 0
years = ['2021']
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
                except Exception:
                    pass
                # create season_df if not initialized
                if not season_df_init:
                    try:
                        season_df = player_seasons
                        season_df_init = 1
                    except Exception:
                        pass
                # else concatenate to season_df
                else:
                    try:
                        season_df = pd.concat([season_df,
                                       player_seasons], axis = 0)
                    except Exception:
                        pass
                if not career_df_init:
                    try:
                        career_df = player_career
                        career_df_init = 1
                    except Exception:
                        pass
                # else concatenate to career_df
                else:
                    try:
                        career_df = pd.concat([career_df,
                                       player_career], axis = 0)
                    except Exception:
                        pass

                # add player to players_collected
                players_collected.append(player_id)
                print(player.name)

season_df = season_df[cols]
season2021 = season_df[season_df['year'] == '2021']
season2021 = season2021.sort_values(by='name',ascending=True)

season_df = season_df.loc[:,~season_df.columns.duplicated()]
season2021 = season2021.loc[:,~season2021.columns.duplicated()]
season2021 = season2021.loc[:, (season2021 != 0).any(axis=0)]

dateString = datetime.strftime(datetime.now(), '%Y_%m_%d')

# gc authorizes and lets us access the spreadsheets
gc = gspread.oauth()

# create the workbook where the day's data will go
# add in folder_id to place it in the folder we want
sh = gc.create(f'2021 Player Data as of {dateString}',folder_id=nhlPlayerFolderId)

# access the first sheet of that newly created workbook
worksheet = sh.get_worksheet(0)

# edit the worksheet with the created dataframe for the day's data
worksheet.update([season2021.columns.values.tolist()] + season2021.values.tolist())

# open the main workbook with that workbook's url
db = gc.open_by_url(playerDashboardURL)

# changed this over to the second sheet so the dashboard can be the first sheet
# dbws is the database worksheet, as in the main workbook that is updated and
# used to analyze and pick from
dbws = db.get_worksheet(1)

# below clears the stock sheet so it can be overwritten with updates
# z1000 is probably overkill but would rather over kill than underkill
range_of_cells = dbws.range('A1:Z1000')
for cell in range_of_cells:
    cell.value = ''
dbws.update_cells(range_of_cells)

# update the stock spreadsheet in the database workbook with the df
dbws.update([season2021.columns.values.tolist()] + season2021.values.tolist())

print(datetime.now()-startTime)
