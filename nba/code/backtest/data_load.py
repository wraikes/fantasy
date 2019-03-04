import pandas as pd, numpy as np, datetime, os
from sklearn.linear_model import Ridge


def extract_date_from_file_name(file):
    tdate = file.split(' ')[-1].replace('.csv', '').replace('_', '-')
    date_str_first = tdate.split('-')[0]
    date_str_second = tdate.split('-')[1]

    if len(date_str_first) == 1:
      date_str_first = '0'+date_str_first
      year = '2019'
    else: 
      year = '2018'

    if len(date_str_second) == 1:
      date_str_second = '0'+date_str_second

    tdate = '{}-{}-{}'.format(year, date_str_first, date_str_second)
    
    return tdate


# def create_optimizer_df(link, date):
#     optimizer_df = pd.DataFrame(columns=[
#                     'Player_Name',
#                     'FDP_predicted',
#                     'Salary',
#                     'Pos',
#                     'Date',
#                     'FDP_error',
#                     'FDP_actual'
#                 ])

#     for file in os.listdir(link):
#         tdate = extract_date_from_file_name(file)

#         if tdate >= date:
#             continue
            
#         tmp = pd.read_csv(link+file)
#         tmp.columns = [x.replace(' ', '_') for x in tmp.columns]
#         tmp.loc[:, 'Date'] = tdate

#         tmp_opt = tmp[[
#             'Player_Name', 'Date', 'Salary', 'Pos'
#         ]]
#         tmp_opt.loc[:, 'FDP_predicted'] = np.nan

#         optimizer_df = optimizer_df.append(tmp_opt, sort=False, ignore_index=True) 

#         optimizer_df['Player_Name'] = optimizer_df['Player_Name'].str.replace('-', ' ')


#         return optimizer_df


def create_historical_df(link, date):
    history_df = pd.DataFrame()

    for file in os.listdir(link):
        tdate = extract_date_from_file_name(file)

        if tdate >= date:
            continue
            
        tmp = pd.read_csv(link+file)
        tmp.columns = [x.replace(' ', '_') for x in tmp.columns]
        tmp.loc[:, 'Date'] = tdate

        #### appned with historical df        
        history_df = history_df.append(tmp, sort=False, ignore_index=True) 

    history_df['Opp_DvP'] = np.where(
      history_df['Opp_DvP'].str.contains('%'), 
      pd.to_numeric(history_df['Opp_DvP'].str.replace('%', '')), 
      0
      )

    history_df['Home'] = np.where(
      history_df['Opp'].str.contains('@'), 
      1, 
      0
      )

    history_df['Player_Name'] = history_df['Player_Name'].str.replace('-', ' ')
    history_df['Player_Name'] = history_df['Player_Name'].str.replace(' Jr', '')
    history_df['Player_Name'] = history_df['Player_Name'].str.replace('.', '')
    history_df['Player_Name'] = history_df['Player_Name'].str.replace("'", '')
    history_df['Player_Name'] = history_df['Player_Name'].str.replace(' III', '')

    history_df['Opp'] = history_df['Opp'].str.replace('@', '')
    history_df.rename(columns={'Position': 'Pos'}, inplace=True)

    for col in ['Likes', 'USG', 'PER', 'Inj']:
      history_df[col] = np.where(history_df[col].isnull(), 0, history_df[col])

    #history_df = injury_columns(history_df)
    #history_df = history_df[history_df.Inj==0]
    #history_df.drop(columns=['Inj'], inplace=True)

    return history_df





















# def injury_columns(df):
#   tmp = df.copy()
#   inj = df[df.Inj != 0][['Player_Name', 'Team', 'Opp', 'Pos', 'Date']]

#   for col in ['Team', 'Pos']: #Player_Name
#       names = inj[col].unique()
#       for name in names:
#         tmp.loc[:, name.replace(' ', '_')+'_injured'] = 0
#         if col != 'Player_Name' :
#               tmp.loc[:, name+"_injured_opp"] = 0

#   for index, row in inj.iterrows():
#     name = row['Player_Name'].replace(' ', '_')
#     team = row['Team']
#     pos = row['Pos']
#     date = row['Date']
#     opp = row['Opp']
    
#     tmp.loc[
#       (tmp.Team==team) & (tmp.Date==date),
#       pos+'_injured'] += 1
#     tmp.loc[
#       (tmp.Opp==opp) & (tmp.Date==date),
#       pos+'_injured_opp'] += 1    
    
#     tmp.loc[
#       (tmp.Team==team) & (tmp.Date==date), 
#       team+'_injured'] += 1
#     tmp.loc[
#       (tmp.Opp==opp) & (tmp.Date==date),
#       team+'_injured_opp'] += 1
    
#     # tmp.loc[
#     #   (tmp.Team==team) & (tmp.Date==date),
#     #   name+'_injured'] = 1

#   return tmp