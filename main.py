from math import floor

import models
from pro_rankings import *

_line_output = "data/output_line.png"
_line_plot_start = "2021-01-01 00:00:00"
_line_plot_end = "2022-12-31 23:59:59"
_bar_output = "data/output_bar.png"
_tourney_output = "data/output_tourney.png"

_bar_number_teams = 12
_rating_diff_days = 7

# Value in days.
_chart_grouping_debounce = 0.5

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Loading plotting libraries ... ")

    import seaborn as sns

    plot_teams = [
        # ("DWG KIA", "#00bcd4"),  # curr lck 1st (cyan)
        # ("Gen.G", "#ffeb3b"),  # curr lck 1st (yellow)
        ("T1", "#f44336"),  # curr lck 1st (red)
        # ("Fnatic", "#ff9800"),  # curr lec 1st (orange)
        # ("MAD Lions", "#ffca28"),  # curr lec 1st (amber)
        ("Rogue (European Team)", "#2196f3"),  # curr lec 1st (blue)
        ("EDward Gaming", "#795548"),  # curr lpl 1st  (brown)
        ("Victory Five", "#cddc39"),  # curr lpl 1st (lime)
        # ("LNG Esports", "#673AB7"),  # curr lpl 1st (deep purple)
        # Note: no LCS teams because they haven't won worlds before. :)
        # Note: colors are the 500 colors from the 2014 Material color palette.
        # Note: the color palette can be found at the link below.
        # https://material.io/design/color/the-color-system.html#tools-for-picking-colors
    ]

    team_names = get_tournaments_teams(MAJOR_LEAGUES)
    majors_data = [(k, v) for k, v in teams_dictionary.items() if k in team_names]

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
    ratings = [t[1].rating for t in majors_data]
    bar_colors = sns.color_palette(palette="hls", n_colors=_bar_number_teams)
    bar_colors = ["#" + "".join((hex(floor(256 * x))[2:] for x in t)) for t in bar_colors]
    ylim_diff = 0.146 * (max(ratings) - min(ratings))

    text = text.replace("{{ labels }}", str(labels))
    text = text.replace("{{ data }}", str(ratings))
    text = text.replace("{{ colors }}", str(bar_colors))
    text = text.replace("{{ yMin }}", str(round(min(ratings) - ylim_diff)))
    text = text.replace("{{ yMax }}", str(round(max(ratings) + ylim_diff)))

    datasets = [{
        "label": t, "backgroundColor": c, "borderColor": c, "showLine": True
    } for t, c in plot_teams]

    for set_ in datasets:
        data = [[models.convert_to_days(d), r]
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
    text = text.replace("{{ progressionStart }}", str(models.convert_to_days(_line_plot_start)))
    text = text.replace("{{ progressionEnd }}", str(models.convert_to_days(_line_plot_end)))

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
                formatted_diff = f'<span style="color: #4CAF50">&plus;{rating_diff}</span>'
            elif rating_diff < 0:
                formatted_diff = f'<span style="color: #F44336">&minus;{-rating_diff}</span>'
            else:
                formatted_diff = ""

            teams_data.append([k, tournament_name, v.rating, formatted_diff])

    for data in teams_data:
        if data[0].endswith(" Team)"):
            data[0] = data[0][:data[0].find("(")]
    teams_data.sort(key=lambda t: t[2], reverse=True)

    template = template.replace("{{ ratingTable }}", "\n".join(
        '            <tr>'
        f'<td style="text-align: right">{i + 1}</td>'
        f'<td class="name">{n}</td>'
        f'<td class="league" style="text-align: center">{l.split("/")[0]}</td>'
        f'<td class="rating" style="text-align: center">{r:.1f}</td>'
        f'<td class="diff" style="text-align: center; white-space: nowrap">{d}</td>'
        '</tr>'
        for i, (n, l, r, d) in enumerate(teams_data))[8:])

    with open("index.html", "w+", encoding="utf-8") as fp:
        fp.write(template)

    print("Done.")
