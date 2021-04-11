from pro_rankings import *

_line_output = "data/output_line.png"
_line_plot_start = "2021-01-08 00:00:00"
_line_plot_end = "2022-01-08 00:00:00"
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
            ("DWG KIA", "#4dd0e1"),  # this worlds 1st  (cyan)
            ("MAD Lions", "#795548"),  # curr lec 1st  (brown)
            ("Royal Never Give Up", "#ffb74d"),  # curr lpl 1st  (orange)
            # ("EDward Gaming", "#795548"),  # curr lpl 1st  (brown)
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

        new_df = pd.DataFrame()
        for team_name in team_names:
            temp_df = df[df["Team"] == team_name]
            temp_df["Date"] = temp_df["Date"].apply(lambda dt: datetime(dt.year, dt.month, dt.day))
            temp_df.drop_duplicates(subset="Date", keep="last", inplace=True)
            temp_df.set_index("Date", inplace=True)
            temp_df = temp_df[temp_df.index > pd.to_datetime(_line_plot_start)]
            temp_df = temp_df.resample("D").interpolate(method="linear")
            temp_df["Team"] = team_name
            new_df = new_df.append(temp_df)
        df = new_df

        # actually plot the data
        print("Generating line graph ... ")

        _, _ = plt.subplots()
        plt.figure(figsize=_plot_size)

        g = sns.lineplot(x="Date", y="Rating", data=df,
                         hue="Team", palette=team_colors, hue_order=team_names)

        plt.xlim(pd.to_datetime(_line_plot_start), pd.to_datetime(_line_plot_end))

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
                if teams_dictionary[team_name].rating > 1800:
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
