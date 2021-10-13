This site displays calculated ratings for professional League of Legends teams.
Only teams from the four major regions are included in the below charts, however
all games are accounted for when calculating the ratings. Due to the nature of
the rating system, the ratings may be very inaccurate at the start of each
season, and generally become more accurate as more games are played.

View the source on [GitHub][2].

[comment]: <> (Ratings of Teams at MSI 2021)
[comment]: <> (----------------------------)
[comment]: <> (This chart displays the ratings of teams at the Mid-Season Invitational of 2021.)
[comment]: <> (Since MSI is the first international competition of the season, ratings at the)
[comment]: <> (start of the tournament will be based heavily on a team's dominance within their)
[comment]: <> (region, so teams from minor regions may have their ratings inflated.)

Ratings of Top Teams
--------------------

This chart displays the calculated ratings for the top teams in the four major
regions ([LCS][3], [LEC][4], [LCK][5], [LPL][6]). The top 12 teams are on this
chart, the remainder can be found in the table below.

[comment]: <> (Note: the top teams from minor leagues may have their ratings inflated if they )
[comment]: <> (dominated their league. This is because if there are no inter-region games, )
[comment]: <> (one's rating is solely based on their performance within their region.)

![image missing](https://raw.githubusercontent.com/xtevenx/ProRankings/master/data/output_bar.png "Ratings of Top Teams")

Rating Progression of Select Teams
----------------------------------

This chart displays the calculated rating progression for select teams. These
teams are chosen by a combination of their performance, personal preference, and
which way the wind happened to be blowing when they were picked.

![image missing](https://raw.githubusercontent.com/xtevenx/ProRankings/master/data/output_line.png "Rating Progression of Select Teams")

Rating List for Major Regions
-----------------------------

This table contains rating data for all major region teams. The RD represents
the "rating deviation", which roughly represents how confident the rating system
is in its rating estimate for that team. Twice the RD signifies the 95%
confidence interval of the rating.

| | Team | Rating | RD |
| --: | --- | :-: | :-: |
| 1 | DWG KIA | 2601.8 | 90.5 |
| 2 | Royal Never Give Up | 2592.6 | 87.3 |
| 3 | EDward Gaming | 2573.7 | 85.2 |
| 4 | FunPlus Phoenix | 2540.2 | 84.9 |
| 5 | LNG Esports | 2482.3 | 71.7 |
| 6 | MAD Lions | 2435.8 | 86.2 |
| 7 | Hanwha Life Esports | 2414.0 | 65.8 |
| 8 | T1 | 2404.0 | 83.8 |
| 9 | Gen.G | 2395.6 | 84.9 |
| 10 | 100 Thieves | 2378.3 | 86.8 |
| 11 | Top Esports | 2358.8 | 71.2 |
| 12 | Suning | 2354.8 | 69.8 |
| 13 | Team WE | 2340.1 | 61.8 |
| 14 | Cloud9 | 2339.0 | 66.0 |
| 15 | Bilibili Gaming | 2318.9 | 73.6 |
| 16 | G2 Esports | 2313.3 | 79.1 |
| 17 | Rare Atom | 2313.0 | 77.3 |
| 18 | Rogue (European Team) | 2311.3 | 90.0 |
| 19 | Afreeca Freecs | 2305.4 | 67.7 |
| 20 | Team Liquid | 2303.6 | 84.0 |
| 21 | TSM | 2289.8 | 69.9 |
| 22 | Misfits Gaming | 2282.8 | 77.4 |
| 23 | Nongshim RedForce | 2280.4 | 71.4 |
| 24 | Fnatic | 2277.8 | 84.2 |
| 25 | Evil Geniuses.NA | 2263.0 | 72.2 |
| 26 | Liiv SANDBOX | 2251.3 | 71.9 |
| 27 | JD Gaming | 2247.3 | 75.8 |
| 28 | KT Rolster | 2247.1 | 69.8 |
| 29 | Oh My God | 2224.9 | 76.1 |
| 30 | Invictus Gaming | 2213.1 | 74.1 |
| 31 | Fredit BRION | 2212.9 | 70.4 |
| 32 | LGD Gaming | 2200.2 | 77.6 |
| 33 | Rogue Warriors | 2192.4 | 80.6 |
| 34 | Immortals | 2185.8 | 78.1 |
| 35 | Team Vitality | 2170.4 | 85.7 |
| 36 | Excel Esports | 2151.2 | 91.9 |
| 37 | Astralis | 2139.4 | 90.9 |
| 38 | Ultra Prime | 2136.9 | 78.0 |
| 39 | Dignitas | 2117.9 | 75.6 |
| 40 | SK Gaming | 2094.1 | 93.9 |
| 41 | DRX | 2081.7 | 75.3 |
| 42 | Golden Guardians | 2077.4 | 85.7 |
| 43 | ThunderTalk Gaming | 2071.0 | 77.9 |
| 44 | FlyQuest | 2042.5 | 82.8 |
| 45 | FC Schalke 04 Esports | 2035.6 | 89.9 |
| 46 | Counter Logic Gaming | 2005.0 | 86.6 |
| 47 | Victory Five | 1944.0 | 86.8 |

About the Rating System
-----------------------

The ratings are calculated using the [Glicko-2][1] rating system.

However, there are some things of note:

*   Each game in Mid-Season Invitationals or World Championships counts for
    twice as much as other games in terms of rating calculations.
*   At the start of each season, the rating deviations are adjusted to be
    equivalent to if there was a year without play. This increases the rating's
    volatility and is done to try to account for season start meta shifts.
*   The average rating is set to the average FIDE standard rating which is, as
    of June 2021, 1645. There is no meaning behind this and is done purely for
    entertainment purposes.

More technical things to note:

*   The rating interval is set to one day, however, the ratings are calculated
    after each game. This induces artificially high rating volatility values,
    but the game has a volatile meta so that's not a bug it's a feature.

### Worlds Pick'em Performance

*   The rating system scored 85/124 in the 2020 World Championships Pick'em.
    This is a score total of 68% which was in the top 5% of players.

Acknowledgements
----------------

Thanks to [Leaguepedia][7] for maintaining and providing the data utilized in
these calculations, and to Mark Glickman for devising the Glicko-2 rating
system.

[1]: http://www.glicko.net/glicko/glicko2.pdf
[2]: https://github.com/xtevenx/ProRankings
[3]: https://lol.fandom.com/wiki/LCS/2021_Season
[4]: https://lol.fandom.com/wiki/LEC/2021_Season
[5]: https://lol.fandom.com/wiki/LCK/2021_Season
[6]: https://lol.fandom.com/wiki/LPL/2021_Season
[7]: https://lol.fandom.com/Help:API_Documentation
