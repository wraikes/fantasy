import pandas as pd, numpy as np, datetime

def predict_FPPG(historical_df, date):
    '''
    Calculate the predicted FPPG for each player based on historical dataframe, 
    for every player and every day up until a certain date.
    
    Input:
        historical dataframe
        date to stop calculations
        
    Output:
        dataframe that consists of predicted FPPG for all players up until input date.
    '''
    start_date = str(historical_df.Date.min()).split(' ')[0]
    end_date = date
    tmp = pd.DataFrame()
    
    start_dates = [int(x) for x in start_date.split('-')]
    end_dates = [int(x) for x in end_date.split('-')]

    start_date = datetime.date(*start_dates)
    end_date = datetime.date(*end_dates)
    delta = datetime.timedelta(days=1)
    
    data = []
    
    while start_date <= end_date:        
        backtest = start_date.strftime("%Y-%m-%d")    
        
        ### Check this before running function.
        if pd.Timestamp(backtest) not in set(historical_df['Date']):  
            start_date += delta 
            print('No games for ', backtest)
            continue

        print(backtest)           
        for name in historical_df['First  Last'].unique():    

            tmp_df = historical_df[
                historical_df.Date < backtest
            ].sort_values(by='Date', ascending=False)
                
                
            #################################
            ##### PREDICTED FPPG  ###########
            #################################
            tmp_df = tmp_df[
                tmp_df['First  Last'] == name
            ]
            
            _FDP_est = tmp_df[tmp_df.Minutes > 0].FDP.mean()  ### PREDICTED FPPG; will be more complex in future.

            #################################
            #################################  
            
            #indicates player hasn't played in any game prior to backtest date.
            if tmp_df.shape[0] == 0:    
                continue
                
            data.append({
                'Nickname': name,
                'FPPG_predicted': _FDP_est,
                'Salary': tmp_df['FD Sal'].values[0],
                'Position': tmp_df['FD pos'].values[0],
                'DATE': pd.to_datetime(backtest)
            })

        start_date += delta
        
    tmp = pd.DataFrame(data).dropna()
    tmp = tmp.merge(
        historical_df[['First  Last', 'Date', 'FDP']], 
        left_on=['Nickname', 'DATE'], 
        right_on=['First  Last', 'Date']
    ).drop(columns=['DATE', 'First  Last'])
    
    tmp.rename(columns={'FDP': 'FPPG_actual'}, inplace=True)
    tmp['FPPG_error'] = tmp['FPPG_actual'] - tmp['FPPG_predicted']
    
    return tmp
