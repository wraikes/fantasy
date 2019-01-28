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


def create_optimizer_df(link, date):
    optimizer_df = pd.DataFrame(columns=[
                    'Player_Name',
                    'FDP_predicted',
                    'Salary',
                    'Pos',
                    'Date',
                    'FDP_error',
                    'FDP_actual'
                ])

    for file in os.listdir(link):
        tdate = extract_date_from_file_name(file)

        if tdate >= date:
            continue
            
        tmp = pd.read_csv(link+file)
        tmp.columns = [x.replace(' ', '_') for x in tmp.columns]
        tmp.loc[:, 'Date'] = tdate

        tmp_opt = tmp[[
            'Player_Name', 'Date', 'Salary', 'Pos'
        ]]
        tmp_opt.loc[:, 'FDP_predicted'] = np.nan

        optimizer_df = optimizer_df.append(tmp_opt, sort=False, ignore_index=True) 

        return optimizer_df


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
        tmp_hist = tmp.drop(columns = [
            'Likes',
            'Inj',
            'USG',
            'PER'
        ])
        
        history_df = history_df.append(tmp_hist, sort=False, ignore_index=True) 

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

    history_df['Opp'] = history_df['Opp'].str.replace('@', '')

    return history_df.rename(columns={'Position': 'Pos'})
