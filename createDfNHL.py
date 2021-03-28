from sportsipy.nhl.teams import Team
from sportsipy.nhl.teams import Teams
import pandas as pd
from datetime import datetime
import getGaNhl
import importlib
from datetime import datetime
import gspread
from nhlSecrets import nhlTeamFolderId, teamDashboardURL

# Done implement gspread functionality

startTime = datetime.now()

print('Running createDfNhl.py')
importlib.reload(getGaNhl)
from nhlColsTeam import cols,correctNames


teams = Teams(year='2021')

# get list of teams to iterate over
abbr_list = []
for team in teams:
    abbr_list.append(team.abbreviation)

# establish dataframe for team stats
league_df = pd.DataFrame()

print('Gathering team statistics.')
# iterate over the abbrevations to get each teams dataframe
for abbr in abbr_list:
    nextTeam = Team(abbr)
    team_df = pd.DataFrame(data=nextTeam.dataframe)
    # concatenate onto the established dataframe
    league_df = pd.concat([league_df,team_df])

# goals against will not pull with sporstipy, using bs4 to do this here
# from the the getGa function imported from getGaNhl

# establish empty df to store that data
ga_df = pd.DataFrame()

# the function creates a list of list, so we appropriately name
ga_listoflists = []

print('Gathering the necessary, missing data.')
# for the abbr_list created before, iterate over and add to the list of lists
for abbr in abbr_list:
    ga_listoflists.append(getGaNhl.getGa(abbr))
    
# for list in the list, add that variable to the ga_list
ga_list=[]
for sublist in ga_listoflists:
    for item in sublist:
        ga_list.append(item)
    
print('Assembling dataframe.')
# get all of that data into int form
ga_list = list(map(int,ga_list))

# populate the df with the abbr and the ga for that team
ga_df = ga_df.assign(team=abbr_list)
ga_df = ga_df.assign(goals_against=ga_list)

# sort dataframes so data is added correctly
ga_df = ga_df.sort_values(by='team',ascending=True)
league_df = league_df.sort_values(by='name',ascending=True)

# drop empty columns/what we dont care about from league_df
league_df = (league_df.drop(
    ['goals_against','pdo_at_even_strength','total_goals_per_game'],axis=1))

# set index
ga_df = ga_df.set_index(league_df.index)
# add goals against to the main df
goals_against = ga_df['goals_against']
league_df = league_df.join(goals_against)

print('Calculating additional data.')
# define variables for EWP calculation
exponent = 2.19
gamesInSeason = 82
decimals = 0

# calculate EWP and all associated
league_df['EWP'] = round(((league_df['goals_for']**exponent)/
((league_df['goals_for']**exponent)+(league_df['goals_against']**exponent))),2)
league_df['PW'] = league_df['games_played'] * league_df['EWP']
league_df['PW'] = league_df['PW'].apply(lambda x: round(x, decimals))
league_df['PL'] = league_df['games_played'] * (1-league_df['EWP'])
league_df['PL'] = league_df['PL'].apply(lambda x: round(x, decimals))
league_df['PW Season'] = gamesInSeason * league_df['EWP']
league_df['PW Season'] = league_df['PW Season'].apply(lambda x: round(x,decimals))
league_df['PL Season'] = gamesInSeason * (1-league_df['EWP'])
league_df['PL Season'] = league_df['PL Season'].apply(lambda x: round(x,decimals))
league_df['Ahead/Behind'] = league_df['wins'] - league_df['PW']

# add some extra coluns unrelated to EWP
league_df['GF/G'] = league_df['goals_for']/league_df['games_played']
league_df['GA/G'] = league_df['goals_against']/league_df['games_played']
league_df['GF/G'] = league_df['GF/G'].apply(lambda x: round(x,2))
league_df['GA/G'] = league_df['GA/G'].apply(lambda x: round(x,2))
league_df['Goal Diff'] = league_df['GF/G']-league_df['GA/G']
league_df['PP Diff'] = (league_df['power_play_goals'] - 
                        league_df['power_play_goals_against'])
league_df['PPO Diff'] = (league_df['power_play_opportunities'] - 
                         league_df['power_play_opportunities_against'])
league_df['Shot Diff'] = league_df['shots_on_goal'] - league_df['shots_against']
league_df['PP Diff'] = league_df['PP Diff'].apply(lambda x: round(x,decimals))
league_df['PPO Diff'] = league_df['PPO Diff'].apply(lambda x: round(x,decimals))
league_df['Shot Diff'] = league_df['Shot Diff'].apply(lambda x: round(x,decimals))

# organize dataframe and put some finishing touches
league_df.reset_index(drop=True, inplace=True)

league_df = league_df[cols]

league_df = league_df.set_axis(correctNames,axis=1,inplace=False)

print('Saving to dataframe.')
# get current date to append to sheet name
dateString = datetime.strftime(datetime.now(), '%Y_%m_%d')

# gc authorizes and lets us access the spreadsheets
gc = gspread.oauth()

# create the workbook where the day's data will go
# add in folder_id to place it in the folder we want
sh = gc.create(f'NHL Team Data as of {dateString}',folder_id=nhlTeamFolderId)

# access the first sheet of that newly created workbook
worksheet = sh.get_worksheet(0)

# edit the worksheet with the created dataframe for the day's data
worksheet.update([league_df.columns.values.tolist()] + league_df.values.tolist())

# open the main workbook with that workbook's url
db = gc.open_by_url(teamDashboardURL)

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

# update the stock spreadsheet in the database workbook with the stock_df
dbws.update([league_df.columns.values.tolist()] + league_df.values.tolist())

print('Script complete.')
print(datetime.now()-startTime)
