import pandas as pd, numpy as np


def make_predictions(model, opt_df, hist_df):  
    optimizer_df = opt_df.copy()
    df = hist_df.copy()

    for date in df.Date.unique():
        tmp_df = df[df.Date <= date].dropna()
        
        if tmp_df[tmp_df.Date < date].shape[0] == 0:
            continue
        
        tmp_df['PlayerName'] = tmp_df['Player_Name']
        tmp_df['Position'] = tmp_df['Pos']
        tmp_df = pd.get_dummies(tmp_df, columns=['PlayerName', 'Position', 'Team', 'Opp'])
        
        X = tmp_df[tmp_df.Date < date].drop(columns=['Actual_FP', 'Date', 'Player_Name', 'Pos']+cols)
        y = tmp_df[tmp_df.Date < date]['Actual_FP']
        
        model.fit(X, y)
        
        preds_df = tmp_df[tmp_df.Date == date]
        
        if preds_df.shape[0] == 0:
            continue
            
        preds = linear.predict(preds_df.drop(columns=['Date', 'Player_Name', 'Pos', 'Actual_FP']+cols))
        preds_df['FDP_predicted'] = preds
        preds_df['FDP_error'] = preds_df['Actual_FP'] - preds_df['FDP_predicted']
        
        preds_df.rename(columns={'Actual_FP': 'FDP_actual'}, inplace=True)
        
        optimizer_df = optimizer_df.append(
            preds_df[[
                'Player_Name',
                'FDP_predicted',
                'Salary',
                'Pos',
                'Date',
                'FDP_error',
                'FDP_actual'
            ]]
        )