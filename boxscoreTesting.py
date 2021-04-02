from sportsipy.nhl.schedule import Schedule
import pandas as pd

detroit_schedule = Schedule('DET')

boxscores = pd.DataFrame()

for game in detroit_schedule:
    # print(game.date)  # Prints the date the game was played
    # print(game.result)  # Prints whether the team won or lost
    # # Creates an instance of the Boxscore class for the game.
    boxscore = game.dataframe
    print(game)
    boxscores = pd.concat([boxscore,boxscores])