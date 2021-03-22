# Calculate r squared to find best relationships
# possibly lambda function?
# DONE: import the dataframe from createDF.py
# DONE: need to make a date string to get the days dataframe
# DONE: do I have to make a whole ass dataframe then do the math?

import pandas as pd
from datetime import datetime
import scipy.stats
from variable import r2List
import os
import numpy as np

startTime = datetime.now()

# get the days date
dateString = datetime.strftime(datetime.now(), '%Y_%m_%d')

# declare the path, this method of the variable and raw string makes the code
# a bit more readable
dataPath = (r'C:\Users\Vincent\Documents\GitHub'
            r'\NHL-Analysis\Team Data'
            r'\Team Stats ' + dateString + '.csv')

# get the data
print('Gathering data.')
league_data_df = pd.read_csv(dataPath)
print('DONE: Data secured.')

league_data_df = league_data_df[r2List]


print('Calculating and printing r2 to wins.')
r2_df_dict = {}

decimals = 2

# for col in league_data_df.columns[3:]:
#     r2 = round((scipy.stats.linregress(league_data_df[['W', col]].to_numpy())
#                 .rvalue ** 2),decimals)
#     print(col + ' ' + ' ' + str(r2))
#     if col not in r2_df_dict.keys():
#         r2_df_dict[col] = r2



for col in league_data_df.columns[3:]:
    correlation_matrix = np.corrcoef(league_data_df['W'],col)
    correlation_xy = correlation_matrix[0,1]
    r2 = correlation_xy**2
    print(col + ' ' + ' ' + str(r2))
    if col not in r2_df_dict.keys():
        r2_df_dict[col] = r2

print('DONE: r2 calculated and printed.')

# DONE: set index so statistic shows in row
print('Organizing dataframe.')
r2_df = pd.DataFrame()
r2_df = r2_df.append(r2_df_dict, ignore_index=True)
r2_df = r2_df.transpose()
r2_df = r2_df.rename(columns={0:'W'})
r2_df = r2_df.sort_values('W',ascending=False)
r2_df = r2_df.reset_index(drop=False)
print('DONE: Dataframe organized.')

print('Saving dataframe to csv.')
os.chdir(r'C:\Users\Vincent\Documents\GitHub\Basketball-Analysis\Excel Sheets')
# os.chdir(r'/home/pi/Documents/Basketball-Analysis/Excel Sheets')
dateString = datetime.strftime(datetime.now(), '%Y_%m_%d')
r2_df.to_csv('R2 Measurements ' + dateString + '.csv',index=False)
print('Saved to csv. Script complete.')

print(datetime.now()-startTime)