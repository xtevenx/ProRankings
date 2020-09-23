from pro_rankings import *

# only plot values after start of season 9.
plot_after = "2019-01-09 00:00:00"

output_file = "data/output_line.png"

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

    print("Loading plotting libraries ... ")

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    sns.set_style("darkgrid")
    plt.figure(figsize=(13.6, 7.65))

    print("Sorting data by date ... ")

    df = pd.DataFrame(plot_data)
    df["Date"] = pd.to_datetime(df["Date"])
    df.sort_values(by="Date", inplace=True)

    # filter data to only include the ones we want.
    df = df[df.Date > pd.to_datetime(plot_after)]

    print("Plotting values onto graph ... ")

    g = sns.lineplot(x="Date", y="Rating", data=df,
                     hue="Team", palette=team_colors, hue_order=team_names)

    print("Saving graph output ... ")

    plt.title("Rating Progression of Select Teams at Worlds 2020")
    plt.tight_layout()

    plt.savefig(output_file, dpi=141.21)

    print("Done.")
