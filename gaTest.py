from sportsipy.nhl.teams import Teams

teams = Teams(year='2021')
for team in teams:
    teams = Teams(year='2021')
    print(team.name)
    print(team.goals_against)  # Prints goals_against