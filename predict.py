import math

import glicko2_utils

if __name__ == "__main__":
    num_games = int(input("Number of games in the series: "))
    assert num_games & 1 == 1

    r_1 = float(input("Rating of Team 1: "))
    d_1 = float(input("Deviation of Team 1: "))
    assert d_1 > 0

    r_2 = float(input("Rating of Team 2: "))
    d_2 = float(input("Deviation of Team 2: "))
    assert d_2 > 0

    win_games = (num_games - 1) // 2 + 1
    win_pct = glicko2_utils.win_pct(r_1, d_1, r_2, d_2)

    result_pct = []
    for x in range(win_games - 1, -1, -1):
        win_ways = math.comb(win_games + x - 1, x)

        pct = win_ways * win_pct**win_games * (1 - win_pct)**x
        result_pct.insert(0, ((win_games, x), pct))
        pct = win_ways * win_pct**x * (1 - win_pct)**win_games
        result_pct.append(((x, win_games), pct))

    print("\nEstimated result chances: ")
    for (w, l), pct in result_pct:
        print(f"- {w} win {l} loss @ {100 * pct:.1f}%")
