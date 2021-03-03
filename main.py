from pro_rankings import *

_line_output = "data/output_line.png"
_line_plot_after = "2019-01-09 00:00:00"
_bar_output = "data/output_bar.png"

_plot_size = (10.11, 5.69)
_plot_dpi = 189.91

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    [t.finalize(current_date) for t in teams_dictionary.values()]

    print("Loading plotting libraries ... ")

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    sns.set_style("darkgrid")

    sns.set(rc={
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

    if "line":
        print("Preparing data for line graph ... ")

        plot_teams = [
            ("DWG KIA", "#00b8d4"),  # this worlds 1st  (cyan)
            ("Suning", "#ffab00"),  # this worlds 2nd  (amber)
            ("FunPlus Phoenix", "#d50000"),  # last worlds 1st  (red)
            ("G2 Esports", "#212121"),  # curr lec 1st  (gray)
            # ("DWG KIA", "#00b8d4"),  # curr lck 1st  (cyan)
            ("EDward Gaming", "#3e2723"),  # curr lpl 1st  (brown)
            # Note: no LCS teams because they haven't won worlds before.
        ]

        team_names, team_colors = zip(*plot_teams)

        plot_data = {"Date": [], "Rating": [], "Team": []}
        for team_name in team_names:
            timestamps, ratings = zip(*teams_dictionary[team_name].rating_history)
            plot_data["Rating"].extend(ratings)
            plot_data["Date"].extend(timestamps)
            plot_data["Team"].extend(len(timestamps) * (team_name,))

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values(by="Date", inplace=True)

        # filter data to only include the ones we want.
        df = df[df.Date > pd.to_datetime(_line_plot_after)]

        # actually plot the data
        print("Generating line graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        g = sns.lineplot(x="Date", y="Rating", data=df,
                         hue="Team", palette=team_colors, hue_order=team_names)

        plt.title("Rating Progression of Select Teams")
        plt.tight_layout()

        plt.savefig(_line_output, dpi=_plot_dpi)
        plt.clf()

    if "bar":
        print("Preparing data bar graph ... ")

        team_names = get_team_names()
        plot_data = {"Rating": [], "Team": []}
        for team_name in team_names:
            try:
                # add to plotting data dictionary
                if teams_dictionary[team_name].rating > 2000:
                    plot_data["Rating"].append(teams_dictionary[team_name].rating)
                    plot_data["Team"].append(team_name)
            except KeyError as err:
                print(f"Error: team `{team_name}' not found.")

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df.sort_values(by="Rating", ascending=False, inplace=True)

        print("Generating bar graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        g = sns.barplot(x="Team", y="Rating", data=df)

        plt.title("Ratings of Top Teams in Major Leagues")
        plt.xticks(rotation=90, fontstretch="condensed")

        bottom, top = plt.ylim()
        top_diff = 0.382 * (top - max(df["Rating"]))
        plt.ylim(min(df["Rating"]) - top_diff, max(df["Rating"]) + top_diff)

        plt.tight_layout()

        plt.savefig(_bar_output, dpi=_plot_dpi)
        plt.clf()

    print("Done.")
