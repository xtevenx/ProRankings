import mwclient
from time import sleep

from models import TeamData, convert_to_days

_MAJOR_LEAGUES = (
    "LCS 2020 Summer",
    "LEC 2020 Summer",
    "LCK 2020 Summer",
    "LPL 2020 Summer"
)


def get_teams_data():
    # get all games after Oct 27, 2009 (release date of LoL)
    interval_start = "2009-10-27 00:00:00"

    # create database access object
    site = mwclient.Site("lol.gamepedia.com", path="/")

    # collect the history of all team renames.
    response = site.api(
        "cargoquery",
        limit="max",
        tables="TeamRenames=TR",
        fields="TR.OriginalName, TR.NewName",
        order_by="TR.Date"
    )

    rename_history = [x.get("title") for x in response.get("cargoquery")]

    team_renames = {}
    for rename in rename_history:
        old_name = rename.get("OriginalName")
        new_name = rename.get("NewName")

        if new_name in team_renames:
            team_renames[old_name] = team_renames[new_name]
        else:
            team_renames[old_name] = new_name

    print(f"Finished gathering {len(team_renames)} team renames ... ")

    sleep(2.0)

    # collect the history of all game results.
    all_data = []
    while True:
        response = site.api(
            "cargoquery",
            limit="max",
            tables="ScoreboardGames=SG",
            fields="SG.DateTime_UTC, SG.Team1, SG.Team2, SG.WinTeam",
            where=f"SG.DateTime_UTC >= '{interval_start}'",
            order_by="SG.DateTime_UTC"
        )

        limits = response.get("limits")
        query_response = response.get("cargoquery")

        for game_data in query_response:
            data_only = game_data.get("title")

            # correct all team names accordingly depending on whether
            # they have been renamed.
            if data_only.get("Team1") in team_renames:
                data_only["Team1"] = team_renames[data_only.get("Team1")]
            if data_only.get("Team2") in team_renames:
                data_only["Team2"] = team_renames[data_only.get("Team2")]
            if data_only.get("WinTeam") in team_renames:
                data_only["WinTeam"] = team_renames[data_only.get("WinTeam")]

            # add data only if
            if data_only.get("DateTime UTC") != interval_start or data_only not in all_data:
                all_data.append(data_only)

        interval_end = all_data[-1].get("DateTime UTC")
        print(f"Collected {len(all_data)} game results ending at {interval_end} ... ")

        # assuming less than "max" games played per time frame.
        if len(query_response) < limits.get("cargoquery") or interval_start == interval_end:
            break
        interval_start = interval_end

        # minimum 2 second delay between requests.
        sleep(2.0)

    # calculate the ratings of each team.
    teams = {}

    for game_data in all_data:
        game_time = game_data.get("DateTime UTC")

        team1 = game_data.get("Team1")
        if team1 not in teams:  # initialize team1 if not seen before
            teams[team1] = TeamData(team1, game_time)
        team1 = teams[team1]

        team2 = game_data.get("Team2")
        if team2 not in teams:  # initialize team2 if not seen before
            teams[team2] = TeamData(team2, game_time)
        team2 = teams[team2]

        # update the ratings of each time accordingly.
        team1.update_rating(team2, team1.name == game_data.get("WinTeam"), game_time)
        team2.update_rating(team1, team2.name == game_data.get("WinTeam"), game_time)

    print("Finished gathering and calculating team data.")
    return teams


def get_team_names(tournaments=_MAJOR_LEAGUES):
    # create database access object
    site = mwclient.Site("lol.gamepedia.com", path="/")

    # iterate through tournaments and collect teams.
    team_names = set()
    for league_name in tournaments:
        response = site.api(
            "cargoquery",
            limit="max",
            tables="TournamentGroups=TG",
            fields="TG.Team",
            where=f"TG.OverviewPage='{league_name}'"
        )

        # add data to the set of all teams.
        query_result = response.get("cargoquery")
        for team_data in query_result:
            if team_data.get("title").get("Team").startswith("TBD "):
                continue
            team_names.add(team_data.get("title").get("Team"))

        # display progress message.
        print(f"Collected {len(query_result)} team names from `{league_name}` ... ")

        # minimum 2 second delay between requests.
        sleep(2.0)

    print(f"Finished gathering {len(team_names)} team names.")
    return team_names


if __name__ == "__main__":
    from datetime import datetime

    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    teams_dictionary = get_teams_data()

    # display the results
    teams_list = [t for t in teams_dictionary.values()
                  if convert_to_days(current_date) - t.last_game < 30]
    [t.finalize(current_date) for t in teams_list]
    teams_list = sorted(teams_list, key=lambda t: -t.rating)

    longest_name = len(max(teams_list, key=lambda t: len(t.name)).name)
    for i, team in enumerate(teams_list):
        beautified_rank = f"{i + 1}.".rjust(3)
        beautified_name = team.name.ljust(longest_name + 2)
        beautified_rating = f"{team.rating:.1f}".rjust(6)
        print(f"{beautified_rank} {beautified_name} {beautified_rating}")
