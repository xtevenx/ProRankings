from math import floor
from pro_rankings import *

_line_output = "data/output_line.png"
_line_plot_start = "2021-01-08 00:00:00"
_line_plot_end = "2022-01-08 00:00:00"
_bar_output = "data/output_bar.png"
_tourney_output = "data/output_tourney.png"

_plot_size = (9.6, 5.4)
_plot_dpi = 200

_bar_number_teams = 12
_line_smooth_factor = 1.5

BAR_CHART = True
LINE_CHART = True
TOURNAMENT_CHART = False
README = True
HTML = True

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("Loading plotting libraries ... ")

    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import seaborn as sns

    # don't warn on chained assignment (hopefully the code is correct :)
    pd.options.mode.chained_assignment = None

    mpl.rcParams.update({
        "axes.axisbelow": True,
        "axes.edgecolor": "#ffffff9f",
        "axes.facecolor": "black",
        "axes.labelcolor": "#ffffff9f",
        "figure.facecolor": "black",
        "grid.color": "#ffffff",
        "grid.alpha": 0.382,
        "patch.linewidth": 0,
        "text.color": "#ffffff9f",
        "xtick.color": "#ffffff9f",
        "ytick.color": "#ffffff9f",
    })

    plt.grid(color="#ffffff9f")

    if LINE_CHART:
        print("Preparing data for line graph ... ")

        plot_teams = [
            ("DWG KIA", "#00bcd4"),  # curr lck 1st  (cyan)
            # ("T1", "#f44336"),  # curr lck 1st (red)
            # ("Gen.G", "#ffeb3b"),  # curr lck 1st (yellow)
            ("MAD Lions", "#ffca28"),  # curr lec 1st (amber)
            # ("Fnatic", "#ff9800"),  # curr lec 1st  (orange)
            ("EDward Gaming", "#795548"),  # curr lpl 1st  (brown)
            ("FunPlus Phoenix", "#ff5722"),  # personal favourite team (deep orange)
            # Note: no LCS teams because they haven't won worlds before. :)
            # Note: colors are the 500 colors from the 2014 Material color palette.
            # Note: the color palette can be found at the link below.
            # https://material.io/design/color/the-color-system.html#tools-for-picking-colors
        ]

        team_names, team_colors = zip(*plot_teams)

        plot_data = {"Date": [], "Rating": [], "Team": []}
        for team_name in team_names:
            timestamps, ratings = zip(*teams_dictionary[team_name].rating_history)
            plot_data["Rating"].extend(ratings)
            plot_data["Date"].extend(timestamps)
            plot_data["Team"].extend(len(timestamps) * (team_name,))

        # input data into a DataFrame
        datetime_start = pd.to_datetime(_line_plot_start)
        no_smooth_start = datetime_start - pd.to_timedelta(52, unit="W")

        df = pd.DataFrame(plot_data)
        df["Date"] = pd.to_datetime(df["Date"])

        new_df = pd.DataFrame()
        for team_name in team_names:
            temp_df = df[df["Team"] == team_name]
            temp_df["Date"] = temp_df["Date"].apply(lambda dt: datetime(dt.year, dt.month, dt.day))
            temp_df.drop_duplicates(subset="Date", keep="last", inplace=True)
            temp_df.set_index("Date", inplace=True)
            temp_df = temp_df.resample("6H").interpolate(method="linear")
            temp_df = temp_df[temp_df.index >= no_smooth_start]

            # apply Gaussian kernel smoothing.
            smoothed_df = temp_df.copy()
            for date in smoothed_df.index[::-1]:
                multipliers = np.exp(
                    -(temp_df.index - date).days ** 2 / (2 * (_line_smooth_factor ** 2))
                )
                multipliers /= np.sum(multipliers)
                if date < datetime_start:
                    break
                smoothed_df.at[date, "Rating"] = np.sum(multipliers * temp_df["Rating"])
            temp_df = smoothed_df

            temp_df = temp_df[temp_df.index >= datetime_start]
            temp_df["Team"] = team_name
            new_df = new_df.append(temp_df)
        df = new_df

        # actually plot the data
        print("Generating line graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        for name, color in plot_teams:
            plt.plot("Rating", data=df[df["Team"] == name], color=color, label=name)
        plt.legend()

        plt.xlim(pd.to_datetime(_line_plot_start), pd.to_datetime(_line_plot_end))
        plt.grid(True, axis="y")

        plt.title("Rating Progression of Select Teams")

        plt.savefig(_line_output, dpi=_plot_dpi)
        plt.clf()

    team_names = get_tournaments_teams(MAJOR_LEAGUES)
    majors_data = [(k, v) for k, v in teams_dictionary.items() if k in team_names]

    all_names = {t[0] for t in majors_data}
    for team_name in team_names:
        if team_name not in all_names:
            print(f"Error: team `{team_name}' not found.")

    majors_data.sort(key=lambda t: t[1].rating, reverse=True)
    majors_data = majors_data[:_bar_number_teams]

    if BAR_CHART:
        plot_data = {
            "Rating": [t[1].rating for t in majors_data],
            "Team": [t[0] for t in majors_data]
        }

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df.sort_values(by="Rating", ascending=False, inplace=True)

        print("Generating bar graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        bar_colors = sns.color_palette(palette="hls", n_colors=_bar_number_teams)
        bars = plt.bar(x="Team", height="Rating", data=df, color=bar_colors)

        plt.title("Ratings of Top Teams in Major Leagues")
        plt.xticks(ticks=[])

        ylim_diff = 0.146 * (max(df["Rating"]) - min(df["Rating"]))
        plt.ylim(min(df["Rating"]) - ylim_diff, max(df["Rating"]) + ylim_diff)
        plt.grid(True, axis="y")

        y_min = plt.ylim()[0]
        for i, a in enumerate(bars):
            plt.gca().text(
                x=a.get_x() + a.get_width() / 2,
                y=plt.ylim()[0] + 0.2 * ylim_diff,
                s=plot_data["Team"][i],
                backgroundcolor="#0000009f",
                color="#ffffff9f",
                horizontalalignment="center",
                rotation="vertical"
            )

        plt.savefig(_bar_output, dpi=_plot_dpi)
        plt.clf()

    if TOURNAMENT_CHART:
        print("Preparing data for tournament bar graph ... ")

        team_names = get_tournaments_teams([
            "2021 Season World Championship/Main Event",
            "2021 Season World Championship/Play-in",
        ])
        teams_data = [(k, v) for k, v in teams_dictionary.items() if k in team_names]

        all_names = {t[0] for t in teams_data}
        for team_name in team_names:
            if team_name not in all_names:
                print(f"Error: team `{team_name}' not found.")

        teams_data.sort(key=lambda t: t[1].rating, reverse=True)

        plot_data = {
            "Rating": [t[1].rating for t in teams_data],
            "Team": [t[0] for t in teams_data]
        }

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df.sort_values(by="Rating", ascending=False, inplace=True)

        print("Generating tournament bar graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        bar_colors = sns.color_palette(palette="hls", n_colors=len(teams_data))
        bars = plt.bar(x="Team", height="Rating", data=df, color=bar_colors)

        plt.title("Ratings of Teams at Worlds 2021")
        plt.xticks(ticks=[])

        ylim_diff = 0.146 * (max(df["Rating"]) - min(df["Rating"]))
        plt.ylim(min(df["Rating"]) - ylim_diff, max(df["Rating"]) + ylim_diff)
        plt.grid(True, axis="y")

        y_min = plt.ylim()[0]
        for i, a in enumerate(bars):
            plt.gca().text(
                x=a.get_x() + a.get_width() / 2,
                y=plt.ylim()[0] + 0.2 * ylim_diff,
                s=plot_data["Team"][i],
                backgroundcolor="#0000009f",
                color="#ffffff9f",
                horizontalalignment="center",
                rotation="vertical"
            )

        plt.savefig(_tourney_output, dpi=_plot_dpi)
        plt.clf()

    if README:
        print("Generating README.md ... ")

        with open("TEMPLATE.md", "r") as fp:
            template = fp.read()

        team_names = get_tournaments_teams(MAJOR_LEAGUES)
        teams_data = [
            (k, v.rating, v.deviation) for k, v in teams_dictionary.items() if k in team_names]
        teams_data.sort(key=lambda t: t[1], reverse=True)

        string_list = [
            f"| {i + 1} | {n} | {r:.1f} | {d:.1f} |" for i, (n, r, d) in enumerate(teams_data)]
        header = "| | Team | Rating | RD |\n| --: | --- | :-: | :-: |\n"
        template = template.replace("{{ RatingTable }}", header + "\n".join(string_list))

        with open("README.md", "w+") as fp:
            fp.write(template)

    if HTML:
        print("Generating README.html ... ")

        with open("assets/js/chart-config.template", "r") as fp:
            text = fp.read()

        labels = [t[0] for t in majors_data]
        ratings = [round(t[1].rating, 1) for t in majors_data]
        bar_colors = sns.color_palette(palette="hls", n_colors=_bar_number_teams)
        bar_colors = ["#" + "".join((hex(floor(256 * x))[2:] for x in t)) for t in bar_colors]
        ylim_diff = 0.146 * (max(ratings) - min(ratings))

        text = text.replace("{{ labels }}", str(labels))
        text = text.replace("{{ data }}", str(ratings))
        text = text.replace("{{ colors }}", str(bar_colors))
        text = text.replace("{{ yMin }}", str(round(min(ratings) - ylim_diff)))
        text = text.replace("{{ yMax }}", str(round(max(ratings) + ylim_diff)))

        team_names = get_tournaments_teams(MAJOR_LEAGUES)
        teams_data = [
            (k, v.rating, v.deviation) for k, v in teams_dictionary.items() if k in team_names]
        teams_data.sort(key=lambda t: t[1], reverse=True)

        with open("assets/js/chart-config.js", "w") as fp:
            fp.write(text)

        with open("TEMPLATE.html", "r", encoding="utf-8") as fp:
            template = fp.read()

        template = template.replace("{{ ratingTable }}", "\n".join(
            '            <tr>'
            f'<td style="text-align: right">{i + 1}</td>'
            f'<td>{n}</td>'
            f'<td style="text-align: center">{r:.1f}</td>'
            f'<td style="text-align: center">{d:.1f}</td>'
            '</tr>'
            for i, (n, r, d) in enumerate(teams_data))[8:])

        with open("README.html", "w+") as fp:
            fp.write(template)

    print("Done.")
