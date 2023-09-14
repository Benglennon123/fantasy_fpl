import pandas as pd
from .player_data import get_player_data
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
