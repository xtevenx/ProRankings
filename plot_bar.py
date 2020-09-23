from pro_rankings import *

output_file = "data/output_bar.png"

if __name__ == "__main__":
    from datetime import datetime

    teams_dictionary = get_teams_data()
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    [t.finalize(current_date) for t in teams_dictionary.values()]

    # display the results
    print("Preparing data for plotting ... ")

    team_names = get_team_names([
        "2020 Season World Championship/Main Event",
        "2020 Season World Championship/Play-in"
    ])

    plot_data = {"Rating": [], "Team": []}
    for team_name in team_names:
        # add to plotting data dictionary
        plot_data["Rating"].append(teams_dictionary[team_name].rating)
        plot_data["Team"].append(team_name)

    print("Loading plotting libraries ... ")

    import matplotlib.pyplot as plt
    import pandas as pd
    import seaborn as sns

    sns.set_style("darkgrid")
    plt.figure(figsize=(18.3, 10.3))

    print("Sorting data by rating ... ")

    df = pd.DataFrame(plot_data)
    df.sort_values(by="Rating", ascending=False, inplace=True)

    print("Plotting values onto graph ... ")

    g = sns.barplot(x="Team", y="Rating", data=df)

    print("Saving graph output ... ")

    plt.title("Rankings of Teams at Worlds 2020")
    plt.xticks(rotation=90, fontstretch="condensed")
    plt.ylim(bottom=1500)
    plt.tight_layout()

    plt.savefig(output_file, dpi=141.21)

    print("Done.")
