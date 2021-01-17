import mwclient
from time import sleep

from models import QueryDelay, TeamData, convert_to_days

# iterable of all the major leagues.
_MAJOR_LEAGUES: tuple = tuple(f"{s} 2020 Summer" for s in ("LCS", "LEC", "LCK", "LPL"))

# how much extra do world championship games count towards one's rating.
_WORLD_CHAMPIONSHIP_BONUS: int = 2

# query delay object (ensures minimum delay between queries).
_QUERY_DELAY: QueryDelay = QueryDelay(2.0)


def get_teams_data():
    # get all games after Oct 27, 2009 (release date of LoL)
    _interval_start: str = "2009-10-27 00:00:00"

    # create database access object
    site: mwclient.Site = mwclient.Site("lol.gamepedia.com", path="/")

    # collect the history of all team renames -------------------------
    rename_history: list[dict] = []
    interval_start: str = _interval_start

    while True:
        _QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="TeamRenames=TR",
            fields="TR.OriginalName, TR.NewName, TR.Date",
            where=f"TR.Date >= '{interval_start}'",
            order_by="TR.Date"
        )

        limits: dict = response.get("limits")
        query_response: dict = response.get("cargoquery")

        interval_end: str = interval_start
        for _t in query_response:
            rename_data: dict = _t.get("title")
            if rename_data not in rename_history:
                rename_history.append(rename_data)
            interval_end = rename_data.get("Date")

        print(f"Collected {len(rename_history)} team renames ending at {interval_end} ... ")

        if len(query_response) < limits.get("cargoquery") or interval_start == interval_end:
            break
        interval_start = interval_end

    print("Processing the collected team renames ... ")

    team_renames: dict = {}
    for rename in reversed(rename_history):
        old_name: str = rename.get("OriginalName")
        new_name: str = rename.get("NewName")

        if new_name in team_renames:
            team_renames[old_name] = team_renames[new_name]
        else:
            team_renames[old_name] = new_name

    print(f"Finished collecting {len(team_renames)} team renames ... ")

    # collect the history of all game results -------------------------
    games_data: list[dict] = []
    interval_start: str = _interval_start

    while True:
        _QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="ScoreboardGames=SG",
            fields="SG.OverviewPage, SG.Team1, SG.Team2, SG.WinTeam, SG.DateTime_UTC",
            where=f"SG.DateTime_UTC >= '{interval_start}'",
            order_by="SG.DateTime_UTC"
        )

        limits: dict = response.get("limits")
        query_response: dict = response.get("cargoquery")

        interval_end: str = interval_start
        for _t in query_response:
            game_data: dict = _t.get("title")

            # correct all team names based on determined rename history
            if game_data.get("Team1") in team_renames:
                game_data["Team1"] = team_renames[game_data.get("Team1")]
            if game_data.get("Team2") in team_renames:
                game_data["Team2"] = team_renames[game_data.get("Team2")]
            if game_data.get("WinTeam") in team_renames:
                game_data["WinTeam"] = team_renames[game_data.get("WinTeam")]

            # add data only if it has not already been added
            if game_data not in games_data:
                games_data.append(game_data)

                # add bonus games for World Championship results
                page_name = game_data.get("OverviewPage").split("/")[0]
                if page_name.find("World Championship") != -1:
                    for _ in range(_WORLD_CHAMPIONSHIP_BONUS):
                        games_data.append(game_data)

            interval_end = game_data.get("DateTime UTC")

        print(f"Collected {len(games_data)} game results ending at {interval_end} ... ")

        if len(query_response) < limits.get("cargoquery") or interval_start == interval_end:
            break
        interval_start = interval_end

    # calculate the ratings of each team ------------------------------
    print("Processing collected game data ... ")

    teams: dict = {}

    for game_data in games_data:
        game_time: str = game_data.get("DateTime UTC")

        team1: str = game_data.get("Team1")
        if team1 not in teams:  # initialize team1 if not seen before
            teams[team1] = TeamData(team1, game_time)
        team1: TeamData = teams[team1]

        team2: str = game_data.get("Team2")
        if team2 not in teams:  # initialize team2 if not seen before
            teams[team2] = TeamData(team2, game_time)
        team2: TeamData = teams[team2]

        # update the ratings of each time accordingly.
        team1.update_rating(team2, team1.name == game_data.get("WinTeam"), game_time)
        team2.update_rating(team1, team2.name == game_data.get("WinTeam"), game_time)

    print("Finished collecting and processing game data.")

    return teams


def get_team_names(tournaments=_MAJOR_LEAGUES):
    # create database access object
    site: mwclient.Site = mwclient.Site("lol.gamepedia.com", path="/")

    # iterate through tournaments and collect teams.
    team_names: set = set()

    for league_name in tournaments:
        _QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="TournamentGroups=TG",
            fields="TG.Team",
            where=f"TG.OverviewPage='{league_name}'"
        )

        # add data to the set of all teams.
        query_result: dict = response.get("cargoquery")
        for _t in query_result:
            team_name = _t.get("title").get("Team")
            if team_name.startswith("TBD "):
                continue
            team_names.add(team_name)

        # display progress for this iteration.
        print(f"Collected {len(query_result)} team names from `{league_name}` ... ")

    print(f"Finished gathering {len(team_names)} team names.")
    return team_names


if __name__ == "__main__":
    from datetime import datetime

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    teams_dictionary = get_teams_data()

    team_names = get_team_names(_MAJOR_LEAGUES)
    # team_names = get_team_names([
    #     "2020 Season World Championship/Main Event",
    #     "2020 Season World Championship/Play-in"
    # ])

    teams_list = [t for t in teams_dictionary.values() if t.name in team_names]
    tuple(t.finalize(current_date) for t in teams_list)
    teams_list = sorted(teams_list, key=lambda t: -t.rating)

    longest_name = len(max(teams_list, key=lambda t: len(t.name)).name)
    for i, team in enumerate(teams_list):
        beautified_rank = f"{i + 1}.".rjust(3)
        beautified_name = team.name.ljust(longest_name + 2)
        beautified_rating = f"{team.rating:.1f}".rjust(6)
        print(f"{beautified_rank} {beautified_name} {beautified_rating}")
