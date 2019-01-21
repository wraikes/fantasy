import pandas as pd, numpy as np, datetime, re
from pulp import *


class Optimizer:
    '''
    This class will develop the optimizer, set the constraints, and metrics for reporting.
    '''
    #Add add'l constraints if needed.    
    def __init__(self, df, salary_cap=60000, max_players=9, pos_removed=None):
        self.df = df.rename(columns={'FPPG_predicted': 'FPPG'})
        self.optimizer = LpProblem('fantasy', LpMaximize)

        self.salary_cap = salary_cap
        self.max_players = max_players
        self.pos_removed = pos_removed
        
        self.optimize_df = None
    

    # def new_optimizer(self, new_df):
    #     self.optimizer = LpProblem('fantasy', LpMaximize)      


    def optimize(self):
        df = self.df.dropna().copy()

        salaries = {}
        points = {} 
        rewards = []
        costs = []
        total_pos = []
        position_constraints = []

        for pos in df.Position.unique():
            df_pos = df[df.Position == pos]
            salary = list(df_pos[["Nickname", "Salary"]].set_index("Nickname").to_dict().values())[0]
            point = list(df_pos[["Nickname", "FPPG"]].set_index("Nickname").to_dict().values())[0]
            salaries[pos] = salary
            points[pos] = point

        pos_num_available = {
            "PG": 2,
            "C": 1,
            "PF": 2,
            "SF": 2,
            "SG": 2
        }  

        if self.pos_removed:
            pos_num_available[self.pos_remove] +- 1

        _vars = {k: LpVariable.dict(k, v, cat="Binary") for k, v in points.items()}  


        # Setting up the reward
        for k, v in _vars.items():
            costs += lpSum([salaries[k][i] * _vars[k][i] for i in v])
            rewards += lpSum([points[k][i] * _vars[k][i] for i in v])
            total_pos += lpSum([1*_vars[k][i] for i in v])
            self.optimizer += lpSum([_vars[k][i] for i in v]) <= pos_num_available[k]

        self.optimizer += lpSum(rewards)
        self.optimizer += lpSum(total_pos) == self.max_players
        self.optimizer += lpSum(costs) <= self.salary_cap

        self.optimizer.solve()


        ############
        score = str(self.optimizer.objective)
        constraints = [str(const) for const in self.optimizer.constraints.values()]

        summary_df = []

        for v in self.optimizer.variables():
            score = score.replace(v.name, str(v.varValue))
            constraints = [const.replace(v.name, str(v.varValue)) for const in constraints]
            if v.varValue != 0:
                summary_df.append(
                    {'Nickname': ' '.join(v.name.split('_')[1:])}
                )

        return pd.DataFrame(summary_df)


class Backtest(Optimizer):
    '''
    This will provide a performance of optimization and strategy function.
    
    Input:
        Optimizer object
        
    Output:
        Backtest performance
    '''

    def __init__(self, Optimizer):
        
        self.optimizer = Optimizer

        self.df = Optimizer.df.copy()
        self.start_date = Optimizer.df.Date.min()              
        self.end_date = Optimizer.df.Date.max()
        
        self.backtest_df = pd.DataFrame()
        self.results = None
            
        
    def create_backtest_df(self):
        delta = datetime.timedelta(days=1)
        
        while self.start_date <= self.end_date:
            date_string = self.start_date.strftime("%Y-%m-%d")            
            tmp = self.df[self.df.Date == date_string]
            
            player_col = 'players_'+date_string
            self.optimizer = Optimizer(tmp)
            self.backtest_df[player_col] = self.optimizer.optimize().Nickname
            
            self.backtest_df = self.backtest_df.merge(
                tmp[['Nickname', 'FPPG', 'FPPG_actual']],
                how='left',
                left_on=player_col,
                right_on='Nickname',
                copy=False
            ).drop(columns='Nickname')
            
            FPPG_predict_col = 'FPPG_predicted_'+date_string
            FPPG_actual_col = 'FPPG_actual_'+date_string
            
            self.backtest_df.rename(columns={
                'FPPG': FPPG_predict_col,
                'FPPG_actual': FPPG_actual_col
            }, inplace=True)
            
            self.start_date += delta


    def backtest_results(self, drop_lowest=True):
        tmp = self.backtest_df.transpose().copy()
        tmp.drop(index=[x for x in tmp.index if 'players' in x], inplace=True)        
        tmp['sum'] = tmp.sum(axis=1)
        
        if drop_lowest==True:
            tmp['min'] = tmp.min(axis=1)
        else:
            tmp['min'] = 0
        
        predicted = tmp.loc[[x for x in tmp.index if 'predict' in x], ['sum', 'min']]
        actual = tmp.loc[[x for x in tmp.index if 'actual' in x], ['sum', 'min']]
        
        predicted['sum'] = predicted['sum'] - predicted['min']
        actual['sum'] = actual['sum'] - actual['min']
        
        predicted.index = [x.split('_')[-1] for x in predicted.index]
        actual.index = [x.split('_')[-1] for x in predicted.index]
        
        self.results = pd.DataFrame({
            'actual_sum': actual['sum'] ,
            'predicted_sum': predicted['sum'],
            'error': actual['sum'] - predicted['sum']
        })