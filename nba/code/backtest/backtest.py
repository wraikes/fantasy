import pandas as pd, numpy as np, datetime, re
from pulp import *


class Optimizer:
    '''
    This class will develop the optimizer, set the constraints, and metrics for reporting.
    '''
    #Add add'l constraints if needed.    
    def __init__(self, df, salary_cap=60000, max_players=9, team_mems=4):
        self.df = df.dropna()
        self.optimizer = LpProblem('fantasy', LpMaximize)

        self.team_mems = team_mems
        self.salary_cap = salary_cap
        self.max_players = max_players

        self.optimize_df = None
        self.teams = df.Team.unique()

        if len(self.teams) >= 4:
            self.low_players = 4000
        else:
            self.low_players = 1

    def optimize(self):
        df = self.df.dropna().copy()

        teams = {}
        salaries = {}
        points = {} 
        rewards = []
        costs = []
        sals = []
        sals_ = []
        total_pos = []
        team_constraints = []

        for team in self.teams:
            df_team = df[df.Team==team]
            df_team.loc[:, 'val'] = 1
            teams[team] = list(df_team[["Player_Name", 'val']].set_index("Player_Name").to_dict().values())[0]

        for pos in df.Pos.unique():
            df_pos = df[df.Pos == pos]
            salary = list(df_pos[["Player_Name", "Salary"]].set_index("Player_Name").to_dict().values())[0]
            point = list(df_pos[["Player_Name", "FDP_predicted"]].set_index("Player_Name").to_dict().values())[0]
            salaries[pos] = salary
            points[pos] = point

        pos_num_available = {
            "PG": 2,
            "C": 1,
            "PF": 2,
            "SF": 2,
            "SG": 2
        }

        _vars = {k: LpVariable.dict(k, v, cat="Binary") for k, v in points.items()}  

        for team in self.teams:
            con = []
            for k, v in _vars.items():
                con += [teams[team][i] * _vars[k][i] for i in v if i in teams[team].keys()]
            self.optimizer += lpSum(con) <= self.team_mems

        for k, v in _vars.items():
            costs += lpSum([salaries[k][i] * _vars[k][i] for i in v])
            rewards += lpSum([points[k][i] * _vars[k][i] for i in v])
            sals += lpSum([salaries[k][i] * _vars[k][i] for i in v if salaries[k][i] < 4000])
            sals_ += lpSum([salaries[k][i] * _vars[k][i] for i in v if salaries[k][i] >= 10000])
            total_pos += lpSum([1*_vars[k][i] for i in v])
            self.optimizer += lpSum([_vars[k][i] for i in v]) <= pos_num_available[k]

        self.optimizer += lpSum(rewards)
        self.optimizer += lpSum(total_pos) == self.max_players
        self.optimizer += lpSum(costs) <= self.salary_cap
        self.optimizer += lpSum(sals) >= self.low_players
        self.optimizer += lpSum(sals_) >= 2

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
                    {'Player_Name': ' '.join(v.name.split('_')[1:])}
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
        self.start_date = pd.to_datetime(Optimizer.df.Date.min())              
        self.end_date = pd.to_datetime(Optimizer.df.Date.max())
        
        self.backtest_df = pd.DataFrame()
        self.results = None
                    
        
    def create_backtest_df(self, team_mems=4):
        delta = datetime.timedelta(days=1)
        
        while self.start_date <= self.end_date:
            date_string = self.start_date.strftime("%Y-%m-%d")            
            tmp = self.df[self.df.Date == date_string]
            player_col = 'players_'+date_string
            self.optimizer = Optimizer(tmp, team_mems=team_mems)
            names = self.optimizer.optimize().Player_Name
            if len(names) < 7:
                self.start_date += delta
                continue
            self.backtest_df.loc[:, player_col] = names
            self.backtest_df = self.backtest_df.merge(
                tmp[['Player_Name', 'FDP_predicted', 'FDP_actual']],
                how='left',
                left_on=player_col,
                right_on='Player_Name',
                copy=False
            ).drop(columns='Player_Name')
            
            FPPG_predict_col = 'FDP_predicted_'+date_string
            FPPG_actual_col = 'FDP_actual_'+date_string
            
            self.backtest_df.rename(columns={
                'FDP_predicted': FPPG_predict_col,
                'FDP_actual': FPPG_actual_col
            }, inplace=True)
            
            self.start_date += delta


    def backtest_results(self, drop_lowest=True):
        tmp = self.backtest_df.transpose().dropna().copy()
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















# import pandas as pd, numpy as np, datetime, re
# from pulp import *


# class Optimizer:
#     '''
#     This class will develop the optimizer, set the constraints, and metrics for reporting.
#     '''
#     #Add add'l constraints if needed.    
#     def __init__(self, df, salary_cap=56500, max_players=8):
#         self.df = df.dropna()
#         self.optimizer = LpProblem('fantasy', LpMaximize)

#         self.salary_cap = salary_cap
#         self.max_players = max_players
#         self.teams = teams

#         self.optimize_df = None
#         self.teams = df.Team.unique()


#     def optimize(self):
#         df = self.df.dropna().copy()

#         salaries = {}
#         points = {} 
#         rewards = []
#         costs = []
#         total_pos = []

#         for pos in df.Pos.unique():
#             df_pos = df[df.Pos == pos]
#             salary = list(df_pos[["Player_Name", "Salary"]].set_index("Player_Name").to_dict().values())[0]
#             point = list(df_pos[["Player_Name", "FDP_predicted"]].set_index("Player_Name").to_dict().values())[0]
#             salaries[pos] = salary
#             points[pos] = point

#         pos_num_available = {
#             "PG": 2,
#             "C": 1,
#             "PF": 2,
#             "SF": 2,
#             "SG": 2
#         }

#         _vars = {k: LpVariable.dict(k, v, cat="Binary") for k, v in points.items()}  


#         # Setting up the reward
#         for k, v in _vars.items():
#             costs += lpSum([salaries[k][i] * _vars[k][i] for i in v])
#             rewards += lpSum([points[k][i] * _vars[k][i] for i in v])
#             total_pos += lpSum([1*_vars[k][i] for i in v])
#             self.optimizer += lpSum([_vars[k][i] for i in v]) <= pos_num_available[k]

#         self.optimizer += lpSum(rewards)
#         self.optimizer += lpSum(total_pos) == self.max_players
#         self.optimizer += lpSum(costs) <= self.salary_cap

#         self.optimizer.solve()


#         ############
#         score = str(self.optimizer.objective)
#         constraints = [str(const) for const in self.optimizer.constraints.values()]

#         summary_df = []

#         for v in self.optimizer.variables():
#             score = score.replace(v.name, str(v.varValue))
#             constraints = [const.replace(v.name, str(v.varValue)) for const in constraints]
#             if v.varValue != 0:
#                 summary_df.append(
#                     {'Player_Name': ' '.join(v.name.split('_')[1:])}
#                 )

#         return pd.DataFrame(summary_df)


# class Backtest(Optimizer):
#     '''
#     This will provide a performance of optimization and strategy function.
    
#     Input:
#         Optimizer object
        
#     Output:
#         Backtest performance
#     '''

#     def __init__(self, Optimizer):
        
#         self.optimizer = Optimizer

#         self.df = Optimizer.df.copy()
#         self.start_date = pd.to_datetime(Optimizer.df.Date.min())              
#         self.end_date = pd.to_datetime(Optimizer.df.Date.max())
        
#         self.backtest_df = pd.DataFrame()
#         self.results = None
            
        
#     def create_backtest_df(self):
#         delta = datetime.timedelta(days=1)
        
#         while self.start_date <= self.end_date:
#             date_string = self.start_date.strftime("%Y-%m-%d")            
#             tmp = self.df[self.df.Date == date_string]
#             player_col = 'players_'+date_string
#             self.optimizer = Optimizer(tmp)
#             names = self.optimizer.optimize().Player_Name
#             if len(names) < 7:
#                 self.start_date += delta
#                 continue
#             self.backtest_df.loc[:, player_col] = names
#             self.backtest_df = self.backtest_df.merge(
#                 tmp[['Player_Name', 'FDP_predicted', 'FDP_actual']],
#                 how='left',
#                 left_on=player_col,
#                 right_on='Player_Name',
#                 copy=False
#             ).drop(columns='Player_Name')
            
#             FPPG_predict_col = 'FDP_predicted_'+date_string
#             FPPG_actual_col = 'FDP_actual_'+date_string
            
#             self.backtest_df.rename(columns={
#                 'FDP_predicted': FPPG_predict_col,
#                 'FDP_actual': FPPG_actual_col
#             }, inplace=True)
            
#             self.start_date += delta


#     def backtest_results(self, drop_lowest=True):
#         tmp = self.backtest_df.transpose().dropna().copy()
#         tmp.drop(index=[x for x in tmp.index if 'players' in x], inplace=True)        
#         tmp['sum'] = tmp.sum(axis=1)
        
#         if drop_lowest==True:
#             tmp['min'] = tmp.min(axis=1)
#         else:
#             tmp['min'] = 0
        
#         predicted = tmp.loc[[x for x in tmp.index if 'predict' in x], ['sum', 'min']]
#         actual = tmp.loc[[x for x in tmp.index if 'actual' in x], ['sum', 'min']]
        
#         predicted['sum'] = predicted['sum'] - predicted['min']
#         actual['sum'] = actual['sum'] - actual['min']
        
#         predicted.index = [x.split('_')[-1] for x in predicted.index]
#         actual.index = [x.split('_')[-1] for x in predicted.index]
        
#         self.results = pd.DataFrame({
#             'actual_sum': actual['sum'] ,
#             'predicted_sum': predicted['sum'],
#             'error': actual['sum'] - predicted['sum']
#         })
