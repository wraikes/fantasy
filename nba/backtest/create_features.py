import pandas as pd, numpy as np, os


def averages(df, cols):
    tmp_df = df.copy()
    
    for i in cols:
        tmp_df[i+'_mean'] = np.nan
        tmp_df[i+'_std'] = np.nan
        
        for date in df.Date.unique():
            tmp = df[
                (df.Date < date) & 
                (df['Actual_Min'] > 0)  ### Better understand how minutes impacts calculations.
            ].copy()

            grp = tmp.groupby('Player_Name')[i].agg(['mean', 'std']).reset_index()
            #grp['Date'] = pd.to_datetime(date)
            grp['Date'] = date

            #tmp_df['Date'] = pd.to_datetime(tmp_df['Date'])
            tmp_df = tmp_df.merge(grp, how='left', on=['Player_Name', 'Date'])

            tmp_df[i+'_std'] = np.where(tmp_df['std'].notnull(), tmp_df['std'], tmp_df[i+'_std'])
            tmp_df[i+'_mean'] = np.where(tmp_df['mean'].notnull(), tmp_df['mean'], tmp_df[i+'_mean'])

            tmp_df.drop(columns=['std', 'mean'], inplace=True)
        
        tmp_df[i+'_mean'].fillna(method='ffill', inplace=True)
        tmp_df[i+'_std'].fillna(method='ffill', inplace=True)


    return tmp_df


def lag(df, cols):
    new_cols = ['Player_Name', 'Date']+[x+'_lag' for x in cols]
    tmp_df = pd.DataFrame(columns=new_cols)

    for name in df.Player_Name.unique():
        tmp = df.loc[df.Player_Name==name, ['Player_Name', 'Date']+cols]
        tmp.columns = new_cols
        tmp['Date'] = tmp.Date.shift(periods=-1)

        tmp_df = tmp_df.append(tmp)

    df = df.merge(tmp_df, how='left', on=['Player_Name', 'Date'], sort=False)

    return df


def poly(df, poly=3):
    tmp = df.copy()

    if poly < 2:
        return df

    for i in range(2, poly+1):
        for col in df.columns:
            if col != 'Actual_FP' and (df[col].dtypes == 'float' or df[col].dtypes == 'int'):
                new_col = '{}_poly_{}'.format(col, i)
                tmp.loc[:, new_col] = df[col] ** i

    return tmp


def dummy(df):

    df['PlayerName'] = df['Player_Name']
    df['Position'] = df['Pos']

    df = pd.get_dummies(df, columns=['PlayerName', 'Position', 'Team', 'Opp'])

    return df

