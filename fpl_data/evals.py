import pandas as pd
from .player_data import get_player_data
from .models import variable_team
import requests as r


def check_teams_performance(player_ids: list, gameweek_num: int) -> pd.DataFrame:
    """Checks how a team would have performed in a certain game week

    :param player_ids: a numpy array of player_ids
    :param gameweek_num: an integer of what gameweek you would like to look at
    returns a dictionary of player_ids mapped to points
    """
    points_map = {}
    for player in player_ids:
        gameweek = pd.DataFrame(get_player_data(player)["history"])
        gameweek = gameweek[gameweek["round"] == gameweek_num]
        if gameweek.shape[0] > 0:
            points = gameweek["total_points"].iloc[0]
        else:
            points = 0

        points_map[player] = points
    return points_map


def get_best_team(gameweek_num: int) -> pd.DataFrame:
    """Retreives the best performing team of that game week

    :param gameweek_num : The gameweek you want to check the best perfoming team for
    returns the best possible team
    """
    df = pd.DataFrame(
        r.get(
            "https://fantasy.premierleague.com/api/dream-team/" + str(gameweek_num)
        ).json()["team"]
    )
    return df


def compare_performance(
    df: pd.DataFrame,
    gameweek_num: int = 1,
    captain_map: dict = {},
    bench_map: dict = {},
):
    df["gameweek_points"] = df["id"].map(
        check_teams_performance(list(df["id"]), gameweek_num)
    )
    df["captain"] = df["id"].map(captain_map).fillna(1).astype(int)
    df["points_adjusted"] = df["gameweek_points"] * df["captain"]
    df["bench"] = df["id"].map(bench_map)
    df["points_adjusted"] = df.apply(
        lambda x: 0 if x["bench"] == 1 else x["points_adjusted"], axis=1
    )
    print("Models Team Performance: " + str(df["points_adjusted"].sum()))
    print("Best Team Performance: " + str(get_best_team(gameweek_num)["points"].sum()))


def get_performance(
    df: pd.DataFrame,
    gameweek_num: int = 1,
    captain_map: dict = {},
    bench_map: dict = {},
):
    df["gameweek_points"] = df["id"].map(
        check_teams_performance(list(df["id"]), gameweek_num)
    )
    df["captain"] = df["id"].map(captain_map).fillna(1).astype(int)
    df["points_adjusted"] = df["gameweek_points"] * df["captain"]
    df["bench"] = df["id"].map(bench_map)
    df["points_adjusted"] = df.apply(
        lambda x: 0 if x["bench"] == 1 else x["points_adjusted"], axis=1
    )
    return df["points_adjusted"].sum()


def calc_avg_weekly_score(
    df: pd.DataFrame,
    captain_map: dict = {},
    bench_map: dict = {},
    gameweek_start: int = 1,
    gameweek_end: int = 4,
) -> int:
    """A function to get the average weekly performance of a team selected by the model"""
    points_list = []
    for i in range(gameweek_start, gameweek_end):
        points_list.append(get_performance(df, i, captain_map, bench_map))

    return sum(points_list) / len(points_list)


def reward_func(
    coeffients: list,
    df: pd.DataFrame,
    include_players: list,
    var_dict: dict,
    captain_map: dict = {},
    bench_map: dict = {},
    gameweek_start: int = 1,
    gameweek_end: int = 4,
):
    if len(coeffients) == len(var_dict):
        for key, value in zip(var_dict.keys(), coeffients):
            var_dict[key] = value
    else:
        print("Number of values does not match the number of keys.")

    team_selected = variable_team(df, var_dict, include_players)
    avg_score = calc_avg_weekly_score(
        team_selected, captain_map, bench_map, gameweek_start, gameweek_end
    )
    return -avg_score
