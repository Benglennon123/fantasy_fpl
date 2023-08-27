from pulp import LpProblem, LpVariable, lpSum, LpMaximize
import pandas as pd
import requests as r 
from .player_data import get_player_data


def base_team(df,inlcude_player_ids)-> pd.DataFrame():
    """" Selects a team based on multiple different criteria 
    
    :param df: a pandas dataframe of all the static player informtion
    :param inlcude_player_ids: a list of player ids that must be in the team 
    returns a dataframe of 15 players for your team
    """
    df['chance_of_playing_next_round'] = df['chance_of_playing_next_round'].astype(int)
    df['total_points_last_season'] = df['total_points_last_season'].astype(int)
    df['ict_index_last_season'] = df['ict_index_last_season'].astype(float)
    df['assists_last_season'] = df['assists_last_season'].astype(float)
    df['avg_points_per_min'] = df['avg_points_per_min'].astype(float).fillna(0)


    df = df[df.chance_of_playing_next_round == 100]
    #removing Raya as he is transfering
    df = df[df.id != 113]
    df = df[df.team != 12]
    df = df.reset_index(drop=True)

    # Set budget constraint and position constraints
    budget = 1000  # Set your budget limit
    positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
    position_counts = {'Goalkeeper': 2, 'Defender': 5, 'Midfielder': 5, 'Attacker': 3}
    max_players_per_team = 3

    # Create a PuLP linear programming problem
    prob = LpProblem("FantasyFootball", LpMaximize)

    # Create LpVariables for player selection
    selected = [LpVariable(f"player_{i}", cat='Binary') for i in range(len(df))]

    # Define the objective function (maximize total points)
    prob += lpSum(selected[i] * df.loc[i, 'total_points_last_season'] for i in range(len(df)))
    

    # Add budget constraint
    prob += lpSum(selected[i] * df.loc[i, 'now_cost'] for i in range(len(df))) <= budget

    # Add position constraints
    for position in positions:
        prob += lpSum(selected[i] for i in range(len(df)) if df.loc[i, 'position'] == position) == position_counts[position]

    # Add constraint for maximum players from the same team
    team_players = {team: lpSum(selected[i] for i in df.index if df.loc[i, 'team'] == team)
                    for team in df['team'].unique()}
    for team, players in team_players.items():
        prob += players <= max_players_per_team

    # Add specific player selections
    if len(inlcude_player_ids)> 0:
        # Add specific player selections based on IDs
        for i in df.index:
            if df.loc[i, 'id'] in inlcude_player_ids:
                prob += selected[i] == 1

    # Solve the problem
    prob.solve()

    # Get the selected players
    selected_players = [df.loc[i] for i in range(len(df)) if selected[i].varValue == 1]


    return pd.DataFrame(selected_players)


    

def variable_team(df,var_list:dict = {},inlcude_player_ids:list = [])-> pd.DataFrame():
    """" Selects a team based on multiple different criteria 
    
    :param df: a pandas dataframe of all the static player informtion
    :param inlcude_player_ids: a list of player ids that must be in the team 
    returns a dataframe of 15 players for your team
    """

    df['chance_of_playing_next_round'] = df['chance_of_playing_next_round'].astype(int)
    df['total_points_last_season'] = df['total_points_last_season'].astype(int)
    df['ict_index_last_season'] = df['ict_index_last_season'].astype(float)
    df['assists_last_season'] = df['assists_last_season'].astype(float)
    df['avg_points_per_min'] = df['avg_points_per_min'].astype(float).fillna(0)


    df = df[df.chance_of_playing_next_round == 100]
    #removing Raya as he is transfering
    df = df[df.id != 113]
    df = df[df.team != 12]
    df = df.reset_index(drop=True)

    # Set budget constraint and position constraints
    budget = 1000  # Set your budget limit
    positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
    position_counts = {'Goalkeeper': 2, 'Defender': 5, 'Midfielder': 5, 'Attacker': 3}
    max_players_per_team = 3

    # Create a PuLP linear programming problem
    prob = LpProblem("FantasyFootball", LpMaximize)

    # Create LpVariables for player selection
    selected = [LpVariable(f"player_{i}", cat='Binary') for i in range(len(df))]

   
   

    # Define the objective function based on selected variables to maximize
    if len(var_list) > 0:
        prob += lpSum(selected[i] * df.loc[i, var] * coeff for i in range(len(df)) for var, coeff in var_list.items())

    
        
    
    # Add budget constraint
    prob += lpSum(selected[i] * df.loc[i, 'now_cost'] for i in range(len(df))) <= budget

    # Add position constraints
    for position in positions:
        prob += lpSum(selected[i] for i in range(len(df)) if df.loc[i, 'position'] == position) == position_counts[position]

    # Add constraint for maximum players from the same team
    team_players = {team: lpSum(selected[i] for i in df.index if df.loc[i, 'team'] == team)
                    for team in df['team'].unique()}
    for team, players in team_players.items():
        prob += players <= max_players_per_team

    # Add specific player selections
    if len(inlcude_player_ids)> 0:
        # Add specific player selections based on IDs
        for i in df.index:
            if df.loc[i, 'id'] in inlcude_player_ids:
                prob += selected[i] == 1

    # Solve the problem
    prob.solve()

    # Get the selected players
    selected_players = [df.loc[i] for i in range(len(df)) if selected[i].varValue == 1]


    return pd.DataFrame(selected_players)


def check_teams_performance(player_ids,gameweek_num:int)-> pd.DataFrame():
    """ Checks how a team would have performed in a certain game week 

    :param player_ids: a numpy array of player_ids
    :param gameweek_num: an integer of what gameweek you would like to look at
    returns a dictionary of player_ids mapped to points
    """
    points_map = {}
    for player in player_ids:
        gameweek = pd.DataFrame(get_player_data(player)['history'])
        gameweek = gameweek[gameweek['round'] == gameweek_num]
        if gameweek.shape[0] > 0:
            points = gameweek['total_points'].iloc[0]
        else:
            points = 0 
        
        points_map[player] = points
    return points_map

def get_best_team(gameweek_num:int):
    """ Retreives the best performing team of that game week 

    :param gameweek_num : The gameweek you want to check the best perfoming team for 
    returns the best possible team
    """
    df = pd.DataFrame(r.get("https://fantasy.premierleague.com/api/dream-team/"+str(gameweek_num)).json()['team'])
    return df 

def compare_performance(df:pd.DataFrame,gameweek_num:int =1):
    df['gameweek_points'] = df['id'].map(check_teams_performance(list(df['id']),gameweek_num))
    captain_map = {
        355:"2"
    }
    bench_map = {
        33:1,
        255:1,
        139:1,
        524:1
    }
    df['captain'] = df['id'].map(captain_map).fillna(1).astype(int)
    df['points_adjusted'] = df['gameweek_points'] * df['captain']
    df['bench'] = df['id'].map(bench_map)
    df['points_adjusted'] = df.apply(lambda x: 0 if x['bench']==1 else x['points_adjusted'],axis=1)
    print("Models Team Performance: "+str(df['points_adjusted'].sum()))
    print("Best Team Performance: "+str(get_best_team(gameweek_num)['points'].sum()))