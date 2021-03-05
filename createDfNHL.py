from sportsipy.nhl.teams import Team
from sportsipy.nhl.teams import Teams
import pandas as pd
from datetime import datetime
from nhlColsTeam import cols
import importlib
from urllib.request import urlopen
from bs4 import BeautifulSoup

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
ga_list = []

for abbr in abbr_list:
    url = 'https://www.hockey-reference.com/teams/' + abbr + '/index.html'
    
    html = urlopen(url)
    
    soup = BeautifulSoup(html,features="lxml")
    
    # get column headers with findAll()
    soup.findAll('tr',limit=2)
    
    # use getText()to extract the text we need into a list
    headers = [th.getText() for th in soup.findAll('tr', limit=2)[0].findAll('th')]
    
    # exclude the first column as we will not need the ranking order from 
    # Sports Reference for the analysis
    headers = headers[1:]
    headers
    
    # avoid the first header row
    rows = soup.findAll('tr')[1:]
    all_stats = [[td.getText() for td in rows[i].findAll('td')]
                for i in range(len(rows))]
    
    team_stats = all_stats[0]
    
    goals_against = team_stats[8]
    goals_against = int(goals_against)
    ga_list.append(goals_against)

ga_df = ga_df.assign(team=abbr_list)
ga_df = ga_df.assign(goals_against=ga_list)

# ga_df = ga_df.sort_values(by='team',ascending=True)
# league_df = league_df.sort_values(by='abbreviation',ascending=True)

league_df = league_df.drop(['goals_against'],axis=1)

# league_df['goals_against'] = ga_df['goals_against']
league_df = league_df.assign(goals_against=ga_list)

exponent = 2.19
gamesInSeason = 82
decimals = 0

league_df['EWP'] = (league_df['goals_for']**exponent)/(((league_df['goals_for']**exponent)+league_df['goals_against']**exponent))

print(datetime.now()-startTime)