from sportsipy.nhl.teams import Team
from sportsipy.nhl.teams import Teams
import pandas as pd
from datetime import datetime
from nhlColsTeam import cols,correctNames
from urllib.request import urlopen
from bs4 import BeautifulSoup
import getGaNhl

startTime = datetime.now()

teams = Teams(year='2021')

# get list of teams to iterate over
abbr_list = []
for team in teams:
    abbr_list.append(team.abbreviation)

# establish dataframe for team stats
league_df = pd.DataFrame()

# iterate over the abbrevations to get each teams dataframe
for abbr in abbr_list:
    nextTeam = Team(abbr)
    team_df = pd.DataFrame(data=nextTeam.dataframe)
    # concatenate onto the established dataframe
    league_df = pd.concat([league_df,team_df])

# goals against will not pull with sporstipy, using bs4 to do this here
ga_df = pd.DataFrame()

teams = Teams(year='2021')
ga_listoflists = []

for abbr in abbr_list:
    ga_listoflists.append(getGaNhl.getGa(abbr))
    
ga_list=[]
for sublist in ga_listoflists:
    for item in sublist:
        ga_list.append(item)
        
ga_list = list(map(int,ga_list))

ga_df = ga_df.assign(team=abbr_list)
ga_df = ga_df.assign(goals_against=ga_list)

ga_df = ga_df.sort_values(by='team',ascending=True)
league_df = league_df.sort_values(by='name',ascending=True)

league_df = (league_df.drop(
    ['goals_against','pdo_at_even_strength','total_goals_per_game'],axis=1))

ga_df = ga_df.set_index(league_df.index)
goals_against = ga_df['goals_against']
league_df = league_df.join(goals_against)
