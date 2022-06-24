import json

import models
from pro_rankings import *

_line_plot_start: str = "2021-01-01 00:00:00"
_line_plot_end: str = "2022-12-31 23:59:59"

_bar_number_teams: int = 12
_rating_diff_days: int = 7

# Value in days.
_chart_data_decimals: int = 1
_chart_grouping_debounce: float = 0.5

# https://material-theme.com/docs/reference/color-palette/
# Selected theme: Deep ocean
COLORS = {
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
BAR_COLORS = [
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

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Loading plotting libraries ... ")

    plot_teams = [
        ("T1", COLORS["red"]),
        ("G2 Esports", COLORS["gray"]),
        ("Royal Never Give Up", COLORS["yellow"]),
        # Note: No LCS teams because they haven't won worlds before. :)
    ]

    team_names = get_tournaments_teams(MAJOR_LEAGUES)
    majors_data = [(k, v) for k, v in teams_dictionary.items()
                   if k in team_names]

    all_names = {t[0] for t in majors_data}
    for team_name in team_names:
        if team_name not in all_names:
            print(f"Error: team `{team_name}' not found.")

    majors_data.sort(key=lambda t: t[1].rating, reverse=True)
    majors_data = majors_data[:_bar_number_teams]

    # Actually generate the HTML ==============================================

    print("Generating README.html ... ")

    with open("assets/js/chart-config.template", "r") as fp:
        text = fp.read()

    labels = [t[0] for t in majors_data]
    ratings = [round(t[1].rating, _chart_data_decimals) for t in majors_data]
    ylim_diff = 0.146 * (max(ratings) - min(ratings))

    text = text.replace("{{ labels }}", str(labels))
    text = text.replace("{{ data }}", str(ratings))
    text = text.replace("{{ colors }}", str(BAR_COLORS))

    text = text.replace(
        "{{ yMin }}",
        str(round(min(ratings) - ylim_diff, _chart_data_decimals)))
    text = text.replace(
        "{{ yMax }}",
        str(round(max(ratings) + ylim_diff, _chart_data_decimals)))

    datasets = [{
        "label": t,
        "backgroundColor": c,
        "borderColor": c,
        "showLine": True
    } for t, c in plot_teams]

    for set_ in datasets:
        data = [[round(models.convert_to_days(d), _chart_data_decimals),
                 round(r, _chart_data_decimals)]
                for d, r in teams_dictionary[set_["label"]].rating_history]

        index = 0
        while True:
            if index + 1 >= len(data):
                break
            if data[index + 1][0] <= data[index][0] + _chart_grouping_debounce:
                data.pop(index)
            else:
                index += 1
        set_["data"] = data

    text = text.replace("{{ progressionDatasets }}", json.dumps(datasets))
    text = text.replace(
        "{{ progressionStart }}",
        str(round(models.convert_to_days(_line_plot_start),
                  _chart_data_decimals)))
    text = text.replace(
        "{{ progressionEnd }}",
        str(round(models.convert_to_days(_line_plot_end),
                  _chart_data_decimals)))

    with open("assets/js/chart-config.js", "w") as fp:
        fp.write(text)

    with open("TEMPLATE.html", "r", encoding="utf-8") as fp:
        template = fp.read()

    teams_data = []
    for tournament_name in PREMIER_LEAGUES:
        team_names = get_tournament_teams(tournament_name)

        diff_limit = models.convert_to_days(current_date)
        for k, v in teams_dictionary.items():
            if k not in team_names:
                continue

            rating_diff = 0
            for d, r in reversed(v.rating_history):
                if diff_limit - models.convert_to_days(d) > _rating_diff_days:
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
