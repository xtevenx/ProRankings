from pro_rankings import *
from models import convert_to_days

# only plot values after start of season 9.
plot_after = "2019-01-09 00:00:00"

# only plot the latest values from the last `n` days.
smooth_factor = 1

output_file = "output3.png"

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    [t.finalize(current_date) for t in teams_dictionary.values()]

    # display the results
    print("Preparing data for plotting ... ")

    plot_teams = [
        ("Top Esports", "#ff3e24"),
        ("JD Gaming", "#d61318"),
        ("G2 Esports", "#000000"),  # ED2025
        # ("Fnatic", "#fe5900"),
        ("DAMWON Gaming", "#34ceb5"),
        # ("Team Liquid", "#0c223f"),
    ]

    team_names, team_colors = zip(*plot_teams)

    plot_data = {"Date": [], "Rating": [], "Team": []}
    for team_name in team_names:
        # smooth the rating history data
        new_history = []
        interval_start, latest_rating = (None, None)
        interval_end = None
        for date, rating in teams_dictionary[team_name].rating_history:
            if interval_start is None:
                interval_start, latest_rating = (date, rating)
            elif convert_to_days(date) < convert_to_days(interval_start) + smooth_factor:
                latest_rating = rating
            else:
                new_history.append((interval_end, latest_rating))
                interval_start, latest_rating = (date, rating)
            interval_end = date
        new_history.append((interval_end, latest_rating))
        teams_dictionary[team_name].rating_history = new_history

        # add to plotting data dictionary
        timestamps, ratings = zip(*teams_dictionary[team_name].rating_history)
        plot_data["Rating"].extend(ratings)
        plot_data["Date"].extend(timestamps)
        plot_data["Team"].extend(len(timestamps) * (team_name,))

    print("Loading plotting libraries ... ")

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    sns.set_style("darkgrid")
    # plt.figure(figsize=(11, 8.5))

    print("Sorting data by date ... ")

    df = pd.DataFrame(plot_data)
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values(by="Date", inplace=True)

    # filter data to only include the ones we want.
    df = df[df.Date > pd.to_datetime(plot_after)]

    print("Plotting values onto graph ... ")

    g = sns.relplot(
        x="Date",
        y="Rating",
        hue="Team",
        palette=team_colors,
        hue_order=team_names,
        kind="line",
        aspect=16 / 9,
        data=df
    )

    print("Saving graph output ... ")

    g.fig.autofmt_xdate()
    plt.savefig(output_file, dpi=314)

    print("Done.")
