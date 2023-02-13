# helpfull? https://lol.fandom.com/wiki/Special:CargoTables

import datetime
import json
import os

import mwclient

from models import QueryDelay, TeamData

# Iterable of all premier leagues by OverviewPage
PREMIER_LEAGUES: list[str] = [
    s.replace("_", " ") for s in (
        "LPL/2023_Season/Spring_Season",
        "LEC/2023_Season/Winter_Season",
        "LCK/2023_Season/Spring_Season",
        "LCS/2023_Season/Spring_Season",
        "PCS/2023_Season/Spring_Season",
        "VCS/2023_Season/Spring_Season",
        "CBLOL/2023_Season/Split_1",
        "LJL/2023_Season/Spring_Season",
        "LLA/2023_Season/Opening_Season",
    )
]

# How much *extra* do interregional games count towards one's rating
INTERREGIONAL_BONUS: int = 1

# Query delay object (ensures minimum delay between queries)
QUERY_DELAY: QueryDelay = QueryDelay(1.0)

# List of [faulty] renames to ignore
IGNORE_RENAMES: list[tuple[str, str]] = [
    ("Cloud9", "Quantic Gaming"),
    ("Evil Geniuses.NA", "Winterfox"),
]

# List of season end dates
# https://www.esportstales.com/league-of-legends/ranked-season-end-date
SEASON_END_DATES_READABLE: list[str] = [
    "Jul 13, 2010",  # season  1
    "Nov 29, 2011",  # season  2
    "Feb  1, 2013",  # season  3
    "Jan 10, 2014",  # season  4
    "Jan 21, 2015",  # season  5
    "Jan 20, 2016",  # season  6
    "Dec  8, 2016",  # season  7
    "Jan 16, 2018",  # season  8
    "Jan 23, 2019",  # season  9
    "Jan 10, 2020",  # season 10
    "Jan  8, 2021",  # season 11
    "Jan  7, 2022",  # season 12
    "Jan  1, 9999",  # end of time
]

MONTHS_STR: dict[str, int] = {
    "Jan": 1,
    "Feb": 2,
    "Mar": 3,
    "Apr": 4,
    "May": 5,
    "Jun": 6,
    "Jul": 7,
    "Aug": 8,
    "Sep": 9,
    "Oct": 10,
    "Nov": 11,
    "Dec": 12,
}

SEASON_END_DATES: list[datetime.datetime] = []
for date in SEASON_END_DATES_READABLE:
    m, d, y = date.split()
    m, d, y = MONTHS_STR[m], int(d[:-1]), int(y)
    SEASON_END_DATES.append(datetime.datetime(y, m, d))


def _load_data(filename: str = "data/past_data.json") -> dict:
    """Get previously retrieved data from file if exists.

    Attempt to read `filename` to get an account of previously retrieved data.
    If the file does not exist, return an empty dictionary.

    :return: dict[
            end_at: str = "YYYY-MM-DD HH:MM:SS",
            rename_history: list[dict[OriginalName: str, NewName: str]],
            games_data: list[dict[Team1: str, Team2: str, WinTeam: str]]
        ]
    """

    try:
        with open(filename, mode="r", encoding="utf-8") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return {}


def _save_data(end_at: str,
               rename_history: list[dict[str, str]],
               games_data: list[dict[str, str]],
               filename: str = "data/past_data.json"):
    """Save retrieved data to file."""

    save_obj = {
        "end_at": end_at,
        "rename_history": rename_history,
        "games_data": games_data
    }

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode="w", encoding="utf-8") as fp:
        json.dump(save_obj, fp, separators=(",", ":"))


def parse_string_datetime(str_: str) -> datetime.datetime:
    return datetime.datetime.strptime(str_, "%Y-%m-%d %H:%M:%S")


def teams_data():
    if past_data := _load_data():
        _interval_start = past_data["end_at"]
        rename_history = past_data["rename_history"]
        games_data = past_data["games_data"]

        # Refresh the most recent 28 days of data in case new things
        # were added.
        start_datetime = parse_string_datetime(_interval_start)
        start_datetime -= datetime.timedelta(days=28)
        while parse_string_datetime(
                rename_history[-1]["Date"]) >= start_datetime:
            rename_history.pop()
        while parse_string_datetime(
                games_data[-1]["DateTime UTC"]) >= start_datetime:
            games_data.pop()

        _interval_start = str(start_datetime)
        seen_games = set(str(sorted(g.values())) for g in games_data)

    else:
        # Get all games after Oct 27, 2009 (release date of LoL)
        _interval_start: str = "2009-10-27 00:00:00"

        # rename_history: list[dict[OriginalName: str, NewName: str]]
        rename_history: list[dict[str, str]] = []

        # games_data: list[dict[Team1: str, Team2: str, WinTeam: str]]
        games_data: list[dict[str, str]] = []

        # seen_games: set["{Team1: str, Team2: str, WinTeam: str}"]
        seen_games: set[str] = set()

    # Create MediaWiki access object
    site: mwclient.Site = mwclient.Site("lol.fandom.com", path="/")

    # Collect the history of all team renames -------------------------
    interval_start: str = _interval_start

    while True:
        QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="TeamRenames=TR",
            fields="TR.OriginalName, TR.NewName, TR.Date",
            where=f"TR.Date >= '{interval_start}'",
            order_by="TR.Date")

        limits: dict = response["limits"]
        query_response: dict = response["cargoquery"]

        interval_end: str = interval_start
        for entry in query_response:
            rename_data: dict = entry["title"]

            # Clean up for when saving data.
            del rename_data["Date__precision"]

            for orig, new in IGNORE_RENAMES:
                if rename_data["OriginalName"] == orig and rename_data[
                        "NewName"] == new:
                    break
            else:
                if rename_data not in rename_history:
                    rename_history.append(rename_data)
                interval_end = rename_data["Date"]

        print(f"Collected {len(rename_history)} team renames "
              f"ending at {interval_end} ... ")

        if len(query_response) < limits["cargoquery"]:
            break
        interval_start = interval_end

    print("Processing the collected team renames ... ")

    team_renames: dict[str, str] = {}
    for rename in reversed(rename_history):
        old_name: str = rename["OriginalName"]
        new_name: str = rename["NewName"]

        if new_name in team_renames:
            team_renames[old_name] = team_renames[new_name]
        else:
            team_renames[old_name] = new_name

    print(f"Finished collecting {len(team_renames)} team renames ... ")

    # Collect the history of all game results -------------------------
    interval_start: str = _interval_start

    while True:
        QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="ScoreboardGames=SG",
            fields="SG.OverviewPage, SG.Team1, SG.Team2, SG.WinTeam,"
            "SG.DateTime_UTC",
            where=f"SG.DateTime_UTC >= '{interval_start}'",
            order_by="SG.DateTime_UTC")

        limits: dict = response["limits"]
        query_response: dict = response["cargoquery"]

        interval_end: str = interval_start
        for entry in query_response:
            game_data: dict = entry.get("title")

            # Clean up for when saving data.
            del game_data["DateTime UTC__precision"]

            # Correct all team names based on determined rename history
            if game_data["Team1"] in team_renames:
                game_data["Team1"] = team_renames[game_data["Team1"]]
            if game_data["Team2"] in team_renames:
                game_data["Team2"] = team_renames[game_data["Team2"]]
            if game_data["WinTeam"] in team_renames:
                game_data["WinTeam"] = team_renames[game_data["WinTeam"]]

            # Add data only if it has not already been added
            if (str_data := str(sorted(game_data.values()))) not in seen_games:
                games_data.append(game_data)
                seen_games.add(str_data)

            interval_end = game_data["DateTime UTC"]

        print(f"Collected {len(games_data)} game results "
              f"ending at {interval_end} ... ")

        if len(query_response) < limits["cargoquery"]:
            break
        interval_start = interval_end

    # Save this data for saving. Technically, this should be the latest
    # value between this `interval_end` and the `interval_end` from the
    # team rename history data but I'm too lazy.
    _interval_end: str = interval_end

    # Calculate the ratings of each team ------------------------------
    print("Processing collected game data ... ")

    # teams: dict[teamName: TeamData]
    teams: dict[str, TeamData] = {}

    season_index: int = 0
    for game_data in games_data:
        game_time: str = game_data["DateTime UTC"]

        # Update stats if new season.
        year, month, day = [int(n) for n in game_time.split()[0].split("-")]
        game_datetime = datetime.datetime(year, month, day)

        if game_datetime > SEASON_END_DATES[season_index]:
            for t in teams.values():
                t.soft_reset_stats()
            season_index += 1

        # Get teams from team names
        t1_name: str = game_data["Team1"]
        if t1_name not in teams:  # Initialize team 1 if not seen before
            teams[t1_name] = TeamData(t1_name, game_time)
        team1: TeamData = teams[t1_name]

        t2_name: str = game_data["Team2"]
        if t2_name not in teams:  # Initialize team 2 if not seen before
            teams[t2_name] = TeamData(t2_name, game_time)
        team2: TeamData = teams[t2_name]

        # Add bonus games for interregion game results
        page_name: str = game_data["OverviewPage"]
        is_interregion = page_name.find("World Championship") != -1
        is_interregion |= page_name.find("Mid-Season Invitational") != -1

        # Update the ratings of each time accordingly.
        for _ in range(1 + is_interregion * INTERREGIONAL_BONUS):
            team1.update_rating(team2, team1.name == game_data["WinTeam"],
                                game_time)
            team2.update_rating(team1, team2.name == game_data["WinTeam"],
                                game_time)

    print("Finished collecting and processing game data.")

    _save_data(_interval_end, rename_history, games_data)
    print("Saved collected data for future use.")

    return teams


def tournaments_teams(tournaments: list[str]) -> set:
    """Get a set of participant team names from a list of tournament names."""

    teams = set()
    for t in tournaments:
        teams |= tournament_teams(t)

    print(f"Finished gathering {len(teams)} team names.")
    return teams


def tournament_teams(tournament: str) -> set:
    """Get the set of participant team names for a tournament name."""

    QUERY_DELAY.ensure_delay()
    response: dict = mwclient.Site("lol.fandom.com", path="/").api(
        "cargoquery",
        limit="max",
        tables="Standings=S",
        fields="S.Team",
        where=f"S.OverviewPage='{tournament}'").get("cargoquery")

    teams = tuple(d["title"]["Team"] for d in response)
    teams = set(t for t in teams if not t.startswith("TBD "))

    print(f"Collected {len(teams)} team names from `{tournament}` ... ")
    return teams


def main() -> None:
    teams = teams_data()

    team_names = tournaments_teams(PREMIER_LEAGUES)
    # team_names = team_names([
    #     "2020 Season World Championship/Main Event",
    #     "2020 Season World Championship/Play-in"
    # ])

    teams_list = [t for t in teams.values() if t.name in team_names]
    teams_list.sort(key=lambda t: t.rating, reverse=True)

    longest_name = max(teams_list, key=lambda t: len(t.name)).name
    for i, team in enumerate(teams_list):
        beautified_rank = f"{i + 1}.".rjust(3)
        beautified_name = team.name.ljust(len(longest_name) + 2)
        beautified_rating = f"{team.rating:.0f}".rjust(4)
        beautified_deviation = f"{team.deviation:.0f}".rjust(3)
        print(f"{beautified_rank} {beautified_name} {beautified_rating}"
              f"(dev: {beautified_deviation})")

    # Calculate average ratings for each major league.
    for league_name in PREMIER_LEAGUES:
        league_teams = tournament_teams(league_name)
        league_teams = [t for t in teams_list if t.name in league_teams]
        avg_rating = sum(t.rating for t in league_teams) / len(league_teams)
        print(f"{league_name} average rating: {avg_rating:.2f}")

    # Calculate the highest ever ratings.
    raw_data = [(t.name, max(t.rating_history, key=lambda t: t[1]))
                for t in teams.values()]
    raw_data.sort(key=lambda t: t[1][1], reverse=True)

    for i, x in enumerate(raw_data[:10]):
        print(f"{str(i + 1).rjust(2)}. {x[0]}: {x[1][1]:.1f}"
              f"@ {x[1][0].split()[0]}")


if __name__ == "__main__":
    main()
