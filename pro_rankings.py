import datetime
import json
import mwclient

from models import QueryDelay, TeamData

# iterable of all the major leagues.
_MAJOR_LEAGUES: tuple = tuple(f"{s}/2021 Season/Summer Season" for s in ("LCS", "LEC", "LCK", "LPL"))

# how much extra do interregional games count towards one's rating.
_INTERREGIONAL_BONUS: int = 1

# query delay object (ensures minimum delay between queries).
_QUERY_DELAY: QueryDelay = QueryDelay(1.0)

# list of [faulty] renames to ignore.
_IGNORE_RENAMES: list = [
    ("Cloud9", "Quantic Gaming"),
    ("Evil Geniuses.NA", "Winterfox"),
]

# list of season end dates.
_SEASON_END_DATES_READABLE: list = [
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
    "Jan  1, 9999",  # end of time
]

_MONTHS_STR: dict = {
    "Jan":  1, "Feb":  2, "Mar":  3,
    "Apr":  4, "May":  5, "Jun":  6,
    "Jul":  7, "Aug":  8, "Sep":  9,
    "Oct": 10, "Nov": 11, "Dec": 12,
}

_SEASON_END_DATES: list = []
for date in _SEASON_END_DATES_READABLE:
    m, d, y = date.split()
    m, d, y = _MONTHS_STR[m], int(d[:-1]), int(y)
    _SEASON_END_DATES.append(datetime.datetime(y, m, d))
_SEASON_END_DATES.append(datetime.datetime.today())


def _get_past_data(filename: str = "data/past_data.json") -> dict:
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
        with open(filename, "r") as fp:
            return json.load(fp)
    except FileNotFoundError:
        return dict()


def _save_past_data(end_at, rename_history, games_data, filename: str = "data/past_data.json"):
    """Save retrieved data to file."""

    save_obj = {"end_at": end_at,
                "rename_history": rename_history,
                "games_data": games_data}

    try:
        with open(filename, "w") as fp:
            json.dump(save_obj, fp, separators=(",", ":"))
    except FileNotFoundError:
        ...


def parse_string_datetime(str_: str) -> datetime.datetime:
    return datetime.datetime.strptime(str_, "%Y-%m-%d %H:%M:%S")


def get_teams_data():
    if past_data := _get_past_data():
        _interval_start = past_data["end_at"]
        rename_history = past_data["rename_history"]
        games_data = past_data["games_data"]

        # Refresh the most recent 14 days of data in case new things were added.
        start_datetime = parse_string_datetime(_interval_start)
        start_datetime -= datetime.timedelta(days=14)
        while parse_string_datetime(rename_history[-1]["Date"]) >= start_datetime:
            rename_history.pop()
        while parse_string_datetime(games_data[-1]["DateTime UTC"]) >= start_datetime:
            games_data.pop()

        _interval_start = str(start_datetime)
        seen_games = set(str(sorted(g.values())) for g in games_data)

    else:
        # get all games after Oct 27, 2009 (release date of LoL)
        _interval_start: str = "2009-10-27 00:00:00"

        # rename_history: list[dict[OriginalName: str, NewName: str]]
        rename_history: list = []

        # games_data: list[dict[Team1: str, Team2: str, WinTeam: str]]
        games_data: list = []

        # seen_games: set["{Team1: str, Team2: str, WinTeam: str}"]
        seen_games: set = set()

    # create database access object
    site: mwclient.Site = mwclient.Site("lol.fandom.com", path="/")

    # collect the history of all team renames -------------------------
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
            del rename_data["Date__precision"]

            for orig, new in _IGNORE_RENAMES:
                if rename_data.get("OriginalName") == orig and \
                        rename_data.get("NewName") == new:
                    break
            else:
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
            del game_data["DateTime UTC__precision"]

            # correct all team names based on determined rename history
            if game_data.get("Team1") in team_renames:
                game_data["Team1"] = team_renames[game_data.get("Team1")]
            if game_data.get("Team2") in team_renames:
                game_data["Team2"] = team_renames[game_data.get("Team2")]
            if game_data.get("WinTeam") in team_renames:
                game_data["WinTeam"] = team_renames[game_data.get("WinTeam")]

            # add data only if it has not already been added
            if (str_data := str(sorted(game_data.values()))) not in seen_games:
                games_data.append(game_data)
                seen_games.add(str_data)

                # add bonus games for World Championship results
                page_name = game_data.get("OverviewPage").split("/")[0]
                if page_name.find("World Championship") != -1:
                    for _ in range(_INTERREGIONAL_BONUS):
                        games_data.append(game_data)
                if page_name.find("Mid-Season Invitational") != -1:
                    for _ in range(_INTERREGIONAL_BONUS):
                        games_data.append(game_data)

            interval_end = game_data.get("DateTime UTC")

        print(f"Collected {len(games_data)} game results ending at {interval_end} ... ")

        if len(query_response) < limits.get("cargoquery") or interval_start == interval_end:
            break
        interval_start = interval_end
    _interval_end: str = interval_end

    # calculate the ratings of each team ------------------------------
    print("Processing collected game data ... ")

    # teams: dict[teamName: TeamData]
    teams: dict = {}

    season_index: int = 0
    for game_data in games_data:
        game_time: str = game_data.get("DateTime UTC")

        # update all rating deviations if new season.
        year, month, day = [int(n) for n in game_time.split()[0].split("-")]
        game_datetime = datetime.datetime(year, month, day)

        if game_datetime > _SEASON_END_DATES[season_index]:
            for t in teams.values():
                t.soft_reset_stats()
            season_index += 1

        # get teams from team names
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

    _save_past_data(_interval_end, rename_history, games_data)
    print("Saved collected data for future use.")

    return teams


def get_team_names(tournaments=_MAJOR_LEAGUES) -> set:
    # create database access object
    site: mwclient.Site = mwclient.Site("lol.fandom.com", path="/")

    # iterate through tournaments and collect teams.
    team_names: set = set()

    for league_name in tournaments:
        _QUERY_DELAY.ensure_delay()
        response: dict = site.api(
            "cargoquery",
            limit="max",
            tables="Standings=S",
            fields="S.Team",
            where=f"S.OverviewPage='{league_name}'"
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
    current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    teams_dictionary = get_teams_data()

    team_names = get_team_names(_MAJOR_LEAGUES)
    # team_names = get_team_names([
    #     "2020 Season World Championship/Main Event",
    #     "2020 Season World Championship/Play-in"
    # ])

    teams_list = [t for t in teams_dictionary.values() if t.name in team_names]
    # teams_list: list[TeamData] = [
    #     t for t in teams_dictionary.values()
    #     if convert_to_days(current_date) - t.last_game < 30 and t.deviation < 100]
    tuple(t.finalize(current_date) for t in teams_list)
    teams_list = sorted(teams_list, key=lambda t: -t.rating)

    longest_name = len(max(teams_list, key=lambda t: len(t.name)).name)
    for i, team in enumerate(teams_list):
        beautified_rank = f"{i + 1}.".rjust(3)
        beautified_name = team.name.ljust(longest_name + 2)
        beautified_rating = f"{team.rating:.1f}".rjust(6)
        beautified_deviation = f"{team.deviation:.1f}".rjust(4)
        print(f"{beautified_rank} {beautified_name} {beautified_rating} ± {beautified_deviation}")
