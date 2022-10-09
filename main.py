import datetime
import json

import models
import pro_rankings as pr

# Plot and table configurations
PLT_DATA_PRECISION: int = 1  # decimal points

PLT_BAR_NUMBER_TEAMS: int = 12

PLT_LINE_START: str = "2021-01-01 00:00:00"
PLT_LINE_END: str = "2022-12-31 23:59:59"
PLT_LINE_RATING_DEBOUNCE: float = 0.5  # days

TBL_RATING_DIFF: int = 7  # days

# https://material-theme.com/docs/reference/color-palette/
# Selected theme: Deep ocean
COLORS: dict[str, str] = {
    "green": "#c3e88d",
    "yellow": "#ffcb6b",
    "blue": "#82aaff",
    "red": "#f07178",
    "purple": "#c792ea",
    "orange": "#f78c6c",
    "cyan": "#89ddff",
    "gray": "#717cb4",
    "white": "#eeffff",
}

# https://meyerweb.com/eric/tools/color-blend
PLT_BAR_COLORS: list[str] = [
    COLORS["red"],
    COLORS["orange"],
    COLORS["yellow"],
    "#ebd576",
    "#d7de82",
    COLORS["green"],
    "#a3c9c6",
    COLORS["blue"],
    "#a59ef5",
    COLORS["purple"],
    "#9c87cf",
    COLORS["gray"],
]

PLT_LINE_TEAMS: list[tuple[str, str]] = [
    ("Gen.G", COLORS["yellow"]),
    ("Rogue (European Team)", COLORS["blue"]),
    ("JD Gaming", COLORS["red"]),
    # Note: No LCS teams because they haven't won worlds before. :)
]

# Miscellaneous constants
CURRENT_DATE = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

if __name__ == "__main__":
    teams = pr.teams_data()

    major_names = pr.tournaments_teams(pr.MAJOR_LEAGUES)
    major_teams = [(k, v) for k, v in teams.items() if k in major_names]

    found_major_teams = {t[0] for t in major_teams}
    for name in major_names:
        if name not in found_major_teams:
            print(f"Error: data for team `{name}' not found.")

    major_teams.sort(key=lambda t: t[1].rating, reverse=True)
    major_teams = major_teams[:PLT_BAR_NUMBER_TEAMS]

    # Actually generate the HTML ==============================================

    print("Generating README.html ... ")

    with open("assets/js/chart-config.template", mode="r",
              encoding="utf-8") as fp:
        text = fp.read()

    labels = [t[0] for t in major_teams]
    ratings = [round(t[1].rating, PLT_DATA_PRECISION) for t in major_teams]

    text = text.replace("{{ labels }}", str(labels))
    text = text.replace("{{ data }}", str(ratings))
    text = text.replace("{{ colors }}", str(PLT_BAR_COLORS))

    ymin = round(2 * min(ratings), -2) // 2
    ymax = round(2 * max(ratings), -2) // 2
    text = text.replace("{{ yMin }}", str(ymin - 50 * (min(ratings) < ymin)))
    text = text.replace("{{ yMax }}", str(ymax + 50 * (max(ratings) > ymax)))

    datasets = [{
        "label": t,
        "backgroundColor": c,
        "borderColor": c,
        "showLine": True
    } for t, c in PLT_LINE_TEAMS]

    for dataset in datasets:
        data = [[
            round(models.convert_to_days(d), PLT_DATA_PRECISION),
            round(r, PLT_DATA_PRECISION),
        ] for d, r in teams[dataset["label"]].rating_history]

        index = 0
        while True:
            if index + 1 >= len(data):
                break
            if data[index + 1][0] <= data[index][0] + PLT_LINE_RATING_DEBOUNCE:
                data.pop(index)
            else:
                index += 1
        dataset["data"] = data

    text = text.replace("{{ progressionDatasets }}", json.dumps(datasets))
    text = text.replace(
        "{{ progressionStart }}",
        str(round(models.convert_to_days(PLT_LINE_START), PLT_DATA_PRECISION)))
    text = text.replace(
        "{{ progressionEnd }}",
        str(round(models.convert_to_days(PLT_LINE_END), PLT_DATA_PRECISION)))

    with open("assets/js/chart-config.js", mode="w", encoding="utf-8") as fp:
        fp.write(text)

    with open("TEMPLATE.html", mode="r", encoding="utf-8") as fp:
        template = fp.read()

    teams_data = []
    for tournament_name in pr.PREMIER_LEAGUES:
        team_names = pr.tournament_teams(tournament_name)

        diff_limit = models.convert_to_days(CURRENT_DATE)
        for k, v in teams.items():
            if k not in team_names:
                continue

            rating_diff = 0
            for d, r in reversed(v.rating_history):
                if diff_limit - models.convert_to_days(d) > TBL_RATING_DIFF:
                    break
                rating_diff = v.rating - r
            rating_diff = round(rating_diff, 1)
            if rating_diff > 0:
                formatted_diff = f'<span style="color: var(--green-color)">&plus;{rating_diff}</span>'
            elif rating_diff < 0:
                formatted_diff = f'<span style="color: var(--red-color)">&minus;{-rating_diff}</span>'
            else:
                formatted_diff = ""

            teams_data.append([k, tournament_name, v.rating, formatted_diff])

    for data in teams_data:
        if data[0].endswith(" Team)"):
            data[0] = data[0][:data[0].find("(")]
    teams_data.sort(key=lambda t: t[2], reverse=True)

    template = template.replace(
        "{{ ratingTable }}", "\n".join(
            '            <tr>'
            f'<td style="text-align: right">{i + 1}</td>'
            f'<td class="name">{n}</td>'
            f'<td class="league" style="text-align: center">{l.split("/")[0]}</td>'
            f'<td class="rating" style="text-align: center">{r:.1f}</td>'
            f'<td class="diff" style="text-align: center; white-space: nowrap">{d}</td>'
            '</tr>' for i, (n, l, r, d) in enumerate(teams_data))[8:])

    with open("index.html", "w+", encoding="utf-8") as fp:
        fp.write(template)

    print("Done.")
