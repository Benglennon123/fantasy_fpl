import requests as r
import pandas as pd 
import numpy as np 
from bs4 import BeautifulSoup



pd.options.mode.chained_assignment = None  # default='warn'

def get_static_data() -> pd.DataFrame():
    """ Makes a call to the fpl API to get all the static information for every player

    returns a pandas dataframe of every player in the league 
    """
    data = r.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    playersdf = pd.DataFrame(data['elements'])
    return playersdf

def get_team_info()-> pd.DataFrame():
    """ Fetches the team code and the corresponding team name

    returns a dictionary of team code to team name 
    """
    data = r.get("https://fantasy.premierleague.com/api/bootstrap-static/").json()
    df = pd.DataFrame(data['teams'])[['id','name']]
    return dict(zip(df['id'], df['name']))
    

def clean_static_data(df) -> pd.DataFrame():
    """ Cleans the data from static df and maps up certain attributes to each player
    :param df : a pandas dataframe containing all static player data
    returns   : a clean version of that dataframe with extra attributes  
    """
    df = df[['id','first_name','web_name','team','team_code','now_cost','photo','total_points','value_season','minutes','ict_index_rank',
    'element_type','bps','influence', 'creativity', 'threat','goals_scored','expected_goals','assists','expected_assists','form','selected_by_percent',
    'selected_rank','chance_of_playing_next_round','chance_of_playing_this_round','expected_goals_per_90', 'expected_assists_per_90', 'influence_rank', 
    'creativity_rank', 'threat_rank']]
    formation_map = {
        1:"Goalkeeper",
        2:'Defender',
        3:"Midfielder",
        4:"Attacker"
    }
    df['position']= df['element_type'].map(formation_map)
    team_map = get_team_info()
    df['team_name']= df['team'].map(team_map)
    df['chance_of_playing_next_round'] = df['chance_of_playing_next_round'].fillna(100.0)
    df['influence_rank'] = df['influence_rank'].fillna(670).astype(int)
    df['selected_by_percent'] = df['selected_by_percent'].fillna(670).astype(float)
    df['creativity_rank'] = df['creativity_rank'].fillna(670).astype(int)
    return df

def get_player_data(player_id):
    """ Fetches the players fixtures and History from the API

    :param player_id : The unique identifier for a player 
    returns a json object of the players data
    """
    data = r.get("https://fantasy.premierleague.com/api/element-summary/{}".format(player_id)).json()
    return data

def handle_player_history(df):
    """ Takes in pandas dataframe player history and retreives useful stats 

    :param df : a dataframe of a players history
    returns useful stats about the players history we can use in our model
    """
    
    

    (average_points,average_minutes,avg_points_per_min,goals_scored_last_season,goals_conceded_last_season,assists_last_season,minutes_last_season,clean_sheets_last_season,
    clean_sheets_last_season,total_points_last_season,ict_index_last_season,influence_last_season,threat_last_season,creativity_last_season,red_cards_last_season,yellow_cards_last_season,
    starts_last_season,saves_last_season,penalties_saved_last_season,penalties_missed_last_season) = [0]*20

    if df.shape[0] >0:
        recent_histdf = df[df['season_name']>= '2020/21']
        if recent_histdf.shape[0] > 2:
            average_points = recent_histdf['total_points'].mean()
            average_minutes = recent_histdf['minutes'].mean()
            avg_points_per_min = average_points/average_minutes
            
        if "2022/23" in df.season_name.values:
            goals_scored_last_season = df[df.season_name == "2022/23"]['goals_scored'].iloc[0]
            goals_conceded_last_season = df[df.season_name == "2022/23"]['goals_conceded'].iloc[0]
            assists_last_season = df[df.season_name == "2022/23"]['assists'].iloc[0]
            minutes_last_season = df[df.season_name == "2022/23"]['minutes'].iloc[0]
            clean_sheets_last_season = df[df.season_name == "2022/23"]['clean_sheets'].iloc[0]
            total_points_last_season = df[df.season_name == "2022/23"]['total_points'].iloc[0]
            ict_index_last_season = df[df.season_name == "2022/23"]['ict_index'].iloc[0]
            influence_last_season = df[df.season_name == "2022/23"]['influence'].iloc[0]
            threat_last_season = df[df.season_name == "2022/23"]['threat'].iloc[0]
            creativity_last_season = df[df.season_name == "2022/23"]['creativity'].iloc[0]
            total_points_last_season = df[df.season_name == "2022/23"]['total_points'].iloc[0]
            red_cards_last_season = df[df.season_name == "2022/23"]['clean_sheets'].iloc[0]
            yellow_cards_last_season = df[df.season_name == "2022/23"]['yellow_cards'].iloc[0]
            starts_last_season = df[df.season_name == "2022/23"]['starts'].iloc[0]
            saves_last_season = df[df.season_name == "2022/23"]['saves'].iloc[0]
            penalties_saved_last_season = df[df.season_name == "2022/23"]['penalties_saved'].iloc[0]
            penalties_missed_last_season = df[df.season_name == "2022/23"]['penalties_missed'].iloc[0]

    return (average_points,average_minutes,avg_points_per_min,goals_scored_last_season,goals_conceded_last_season,assists_last_season,minutes_last_season,clean_sheets_last_season,
    clean_sheets_last_season,total_points_last_season,ict_index_last_season,influence_last_season,threat_last_season,creativity_last_season,red_cards_last_season,yellow_cards_last_season,
    starts_last_season,saves_last_season,penalties_saved_last_season,penalties_missed_last_season)


def player_stats(player_id):
    """ Derives extra stats from a players history as well as upcoming fixtures

    :param player_id : The id for the player we are currently trying to get extra stats of
    returns a list of extra stats for the player
    """

    data = get_player_data(player_id)
    fixture_data = pd.DataFrame(data['fixtures'])
    player_history = pd.DataFrame(data['history_past'])


    (average_points,average_minutes,avg_points_per_min,goals_scored_last_season,goals_conceded_last_season,assists_last_season,minutes_last_season,clean_sheets_last_season,
    clean_sheets_last_season,total_points_last_season,ict_index_last_season,influence_last_season,threat_last_season,creativity_last_season,red_cards_last_season,yellow_cards_last_season,
    starts_last_season,saves_last_season,penalties_saved_last_season,penalties_missed_last_season) = handle_player_history(player_history)
        
    return (average_points,average_minutes,avg_points_per_min,goals_scored_last_season,goals_conceded_last_season,assists_last_season,minutes_last_season,clean_sheets_last_season,
    clean_sheets_last_season,total_points_last_season,ict_index_last_season,influence_last_season,threat_last_season,creativity_last_season,red_cards_last_season,yellow_cards_last_season,
    starts_last_season,saves_last_season,penalties_saved_last_season,penalties_missed_last_season)

def get_fixtures()-> pd.DataFrame():
    """ Gets a list of all upcoming fixtures

    returns a dataframe of all upcoming fixtures
    """
    df = pd.DataFrame(r.get('https://fantasy.premierleague.com/api/fixtures').json())
    return df 

def get_win_percentage(uuid:str)-> float:
    """ Given a fixture id and whether the team is home or not will calculate the win percentage of the game 

    :param id: fixture id of the game 
    :param is_home: whether the team is home or not 
    returns a float value of the chance of that team winning that fixture 
    """
    
    fixtures = get_fixtures()
    fixtures = fixtures[fixtures.id == uuid]
    response = r.get("https://www.premierleague.com/match/"+str(fixtures['pulse_id'].iloc[0]))
    soup = BeautifulSoup(response.text, "html.parser")
    result_list = [element.text for element in soup.find_all(class_="count")]
    
    stats = pd.DataFrame([[0,0,0,0,0,0]],columns=['h_total_wins','h_home_wins','h_away_wins','a_total_wins','a_home_wins','a_away_wins'])
    if len(result_list) > 0: 
        #Removing luton from the history as its there first time in the prem
        if len(fixtures[(fixtures.team_a == 12)|(fixtures.team_h == 12)]) != 1:
            stats = pd.DataFrame([result_list],columns=['h_total_wins','h_home_wins','h_away_wins','a_total_wins','a_home_wins','a_away_wins'])
    
        
        
    if (int(stats['h_total_wins']) + int(stats['a_total_wins']))  > 0:
        stats['h_win_perc'] = int(stats['h_total_wins']) / (int(stats['h_total_wins']) + int(stats['a_total_wins']))
        stats['a_win_perc'] = int(stats['a_total_wins']) / (int(stats['h_total_wins']) + int(stats['a_total_wins']))
    else:
        stats['h_win_perc'] = np.nan
        stats['a_win_perc'] = np.nan
    return stats['h_win_perc'].iloc[0],stats['a_win_perc'].iloc[0]

def apply_win_perc()->pd.DataFrame():
    """ a function that for all upcoming fixtures calculates the win percentage of that game 
    """
    df = get_fixtures()
    df[['home_win_perc', 'away_win_perc']] = df['id'].apply(lambda x: pd.Series(get_win_percentage(x)))
    return df 


def apply_win_to_players(fixturesdf:pd.DataFrame(),playersdf:pd.DataFrame(),num_games:int = 10):
    team_map = {}
    fixturesdf = fixturesdf.dropna(subset=['home_win_perc','away_win_perc'])
    fixturesdf = fixturesdf[fixturesdf.finished == False]
    for team_id in playersdf['team'].drop_duplicates():
        team_fixtures = fixturesdf[(fixturesdf.team_a == team_id)|(fixturesdf.team_h == team_id)].head(num_games)
        win_perc_list = []
        for game_id in team_fixtures['code']:
            current_fixture = team_fixtures[team_fixtures.code == game_id]
            if current_fixture['team_h'].iloc[0] == team_id:
                win_perc_list.append(current_fixture['home_win_perc'])
            else:
                win_perc_list.append(current_fixture['away_win_perc'])

        average_win_perc = np.mean(win_perc_list)
        team_map[team_id] = average_win_perc

    playersdf[f'average_win_perc_first_10'] = playersdf['team'].map(team_map)
    return playersdf


def get_curated_player_data()-> pd.DataFrame():
    """ Gets the curated player data with extra Historical stats

    returns a pandas dataframe of curated player data ready to be fed into our model
    """
    df = clean_static_data(get_static_data())
    data = np.transpose(np.array(list(df.apply(lambda x: player_stats(x['id']),axis = 1 ))))
    var_list = ['average_points','average_minutes','avg_points_per_min','goals_scored_last_season','goals_conceded_last_season',
                'assists_last_season','minutes_last_season','clean_sheets_last_season','clean_sheets_last_season',
                'total_points_last_season','ict_index_last_season','influence_last_season','threat_last_season','creativity_last_season',
                'red_cards_last_season','yellow_cards_last_season','starts_last_season','saves_last_season','penalties_saved_last_season','penalties_missed_last_season']
    index = 0 
    for x in var_list:
        df[x] = data[index]
        index = index + 1

    df = apply_win_to_players(apply_win_perc(),df)
    return df







