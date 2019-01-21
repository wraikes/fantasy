import pandas as pd, numpy as np

def prepare_data(historical_path, daily_df_path):
    #clean daily dataframe
    daily_df = pd.read_csv(daily_df_path)
    
    daily_df = daily_df.loc[
        daily_df['Injury Indicator'].isnull(), 
        ['Nickname', 'Position', 'Salary', 'FPPG']
    ]  
    
    #clean historical dataframe
    history_df = pd.read_csv(historical_path, sep=':')    
    history_df.Date = pd.to_datetime(history_df.Date.astype('str'), format="%Y-%m-%d", exact=False)
    history_df['FD pos'] = np.where(history_df['FD pos'] == 1, 'PG',
                               np.where(history_df['FD pos'] == 2, 'SG',
                                   np.where(history_df['FD pos'] == 3, 'SF',
                                       np.where(history_df['FD pos'] == 4, 'PF', 'C')))
                                   )
    
    history_df = history_df[
        (history_df.active == 1)
    ]
        
    return history_df, daily_df
    