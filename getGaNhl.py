from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
from sportsipy.nhl.teams import Teams

teams = Teams(year='2021')
abbr_list = []
for team in teams:
    abbr_list.append(team.abbreviation)

# https://towardsdatascience.com/web-scraping-nba-stats-4b4f8c525994
def getGa(abbr):
    ga_df = pd.DataFrame()
    
    # teams = Teams(year='2021')
    ga_list = []
    abbr_list = []
    # for team in teams:
    #     abbr_list.append(team.abbreviation)
    
    # for abbr in abbr_list:
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
    
    all_stats2 = [e for e in all_stats if e]
    all_stats3=[x for x in all_stats2 if len(x)>3]
    
    team_stats = all_stats3[0]
    
    goals_against = team_stats[8]
    
    ga_list.append(goals_against)
    
    ga_df = ga_df.assign(team=abbr_list)
    ga_df = ga_df.assign(goals_against=ga_list)
    
    return (ga_list)

if __name__ == '__main__':
    getGa()