from pro_rankings import *

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    [t.finalize(current_date) for t in teams_dictionary.values()]

    print("Loading plotting libraries ... ")

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    if "line":
        # only plot values after start of season 9.
        plot_after = "2019-01-09 00:00:00"

        # display the results
        print("Preparing data for plotting line graph ... ")

        plot_teams = [
            ("Top Esports", "#ff3e24"),
            ("JD Gaming", "#d61318"),
            ("G2 Esports", "#000000"),
            ("DAMWON Gaming", "#34ceb5"),
        ]

        team_names, team_colors = zip(*plot_teams)

        plot_data = {"Date": [], "Rating": [], "Team": []}
        for team_name in team_names:
            # add to plotting data dictionary
            timestamps, ratings = zip(*teams_dictionary[team_name].rating_history)
            plot_data["Rating"].extend(ratings)
            plot_data["Date"].extend(timestamps)
            plot_data["Team"].extend(len(timestamps) * (team_name,))

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df["Date"] = pd.to_datetime(df["Date"])
        df.sort_values(by="Date", inplace=True)

        # filter data to only include the ones we want.
        df = df[df.Date > pd.to_datetime(plot_after)]

        # actually plot the data
        sns.set_style("darkgrid")
        plt.figure(figsize=(10.11, 5.69))

        print("Plotting values onto line graph ... ")

        g = sns.lineplot(x="Date", y="Rating", data=df,
                         hue="Team", palette=team_colors, hue_order=team_names)

        print("Saving line graph output ... ")

        plt.title("Rating Progression of Select Teams at Worlds 2020")
        plt.tight_layout()

        plt.savefig("data/output_line.png", dpi=189.91)
        plt.clf()

    if "bar":
        # display the results
        print("Preparing data for plotting bar graph ... ")

        team_names = get_team_names([
            "2020 Season World Championship/Main Event",
            "2020 Season World Championship/Play-in"
        ])

        plot_data = {"Rating": [], "Team": []}
        for team_name in team_names:
            # add to plotting data dictionary
            plot_data["Rating"].append(teams_dictionary[team_name].rating)
            plot_data["Team"].append(team_name)

        # input data into a DataFrame
        df = pd.DataFrame(plot_data)
        df.sort_values(by="Rating", ascending=False, inplace=True)

        sns.set_style("darkgrid")
        plt.figure(figsize=(10.11, 5.69))

        print("Plotting values onto bar graph ... ")

        g = sns.barplot(x="Team", y="Rating", data=df)

        print("Saving bar graph output ... ")

        plt.title("Ratings of Teams at Worlds 2020")
        plt.xticks(rotation=90, fontstretch="condensed")
        plt.ylim(bottom=1500)
        plt.tight_layout()

        plt.savefig("data/output_bar.png", dpi=189.91)
        plt.clf()

    print("Done.")
