import pandas as pd, numpy as np, os


def averages(df, cols):
    tmp_df = df.copy()
    
    for i in cols:
        tmp_df[i+'_mean'] = np.nan
        tmp_df[i+'_std'] = np.nan
        
        for date in df.sort_values(by='Date').Date.unique():
            tmp = df[
                (df.Date < date) & 
                (df['Actual_Min'] > 0)  ### Better understand how minutes impacts calculations.
            ].copy()

            grp = tmp.sort_values(by='Date').groupby('Player_Name')[i].agg(['mean', 'std']).reset_index().fillna(method='ffill')
            #grp['Date'] = pd.to_datetime(date)
            grp['Date'] = date

            #tmp_df['Date'] = pd.to_datetime(tmp_df['Date'])
            tmp_df = tmp_df.merge(grp, how='left', on=['Player_Name', 'Date'])

            tmp_df[i+'_std'] = np.where(tmp_df['std'].notnull(), tmp_df['std'], tmp_df[i+'_std'])
            tmp_df[i+'_mean'] = np.where(tmp_df['mean'].notnull(), tmp_df['mean'], tmp_df[i+'_mean'])

            tmp_df.drop(columns=['std', 'mean'], inplace=True)

    return tmp_df


def lag(df, cols, num=1):
    for lag in range(1, num+1):
        new_cols = ['Player_Name', 'Date']+['{}_lag_{}'.format(x, lag) for x in cols]
        tmp_df = pd.DataFrame(columns=new_cols)

        for name in df.Player_Name.unique():
            tmp = df.loc[df.Player_Name==name, ['Player_Name', 'Date']+cols].sort_values(by='Date')
            tmp.columns = new_cols
            tmp['Date'] = tmp.Date.shift(periods=-lag)

            tmp_df = tmp_df.append(tmp)

        df = df.merge(tmp_df, how='left', on=['Player_Name', 'Date'], sort=False)

    return df

def mean_revert(df, cols, lag=1):
    tmp = df.copy()

    for col in cols:
        if 'Actual_' in col:
            for i in range(1, lag+1):
                tmp['{}_revert_{}'.format(col, i)] = (tmp['{}_lag_{}'.format(col, i)] - tmp[col+'_mean']) / tmp[col+'_std']
                tmp['{}_revert_{}'.format(col, i)] = np.where(
                    tmp['{}_revert_{}'.format(col, i)]**2 == np.inf, 
                    np.nan, 
                    tmp['{}_revert_{}'.format(col, i)]
                )
    return tmp

def poly(df, cols, poly=2):
    tmp = df.copy()

    if poly < 2:
        return df

    for i in range(2, poly+1):
        for col in df.columns:
            if col not in cols and '_injured' not in col and (df[col].dtypes == 'float' or df[col].dtypes == 'int'):
                new_col = '{}_poly_{}'.format(col, i)
                tmp.loc[:, new_col] = df[col] ** i

    return tmp


def dummy(df):

    df['PlayerName'] = df['Player_Name']
    df['Position'] = df['Pos']
    df['Team_'] = df['Team']

    df = pd.get_dummies(df, columns=['PlayerName', 'Position', 'Team_', 'Opp'])

    return df

def injury_columns(df):
    tmp = df[df.Inj != 0].groupby([
        'Team', 
        'Date', 
        'Pos'])['Actual_Min_mean'].sum().unstack().reset_index().fillna(0)

    tmp.rename(columns={
      'C': 'C_out',
      'PF': 'PF_out',
      'PG': 'PG_out',
      'SF': 'SF_out',
      'SG': 'SG_out'
    }, inplace=True)

    df = df.merge(tmp, on=['Team', 'Date'], how='left')

    tmp = df[df.Inj != 0].groupby([
        'Team', 
        'Date', 
        'Pos'])['Actual_FP_mean'].sum().unstack().reset_index().fillna(0)

    tmp.rename(columns={
      'C': 'C_out_fp',
      'PF': 'PF_out_fp',
      'PG': 'PG_out_fp',
      'SF': 'SF_out_fp',
      'SG': 'SG_out_fp'
    }, inplace=True)

    df = df.merge(tmp, on=['Team', 'Date'], how='left')

    return df
    
# def interactions(df, cols):
#     tmp = df.copy()

#     for col_i in df.columns:
#         if col_i in cols or df[col_i].dtypes == 'O':
#             continue

#         for col_j in df.columns:
#             if col_j in cols or df[col_j].dtypes == 'O':
#                 continue

#             if col_i == col_j:
#                 continue

#             tmp[col_i+'__'+col_j] = df[col_i]*df[col_j]

#     return tmp



