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
is in its rating estimate for that team.

| | Team | Rating | RD |
| --: | --- | :-: | :-: |
| 1 | FunPlus Phoenix | 2578.8 | 77.3 |
| 2 | DWG KIA | 2536.9 | 73.7 |
| 3 | MAD Lions | 2507.2 | 80.2 |
| 4 | Royal Never Give Up | 2459.5 | 74.5 |
| 5 | EDward Gaming | 2452.0 | 73.1 |
| 6 | Team WE | 2408.4 | 64.1 |
| 7 | T1 | 2394.5 | 68.2 |
| 8 | LNG Esports | 2362.7 | 63.6 |
| 9 | Rare Atom | 2361.7 | 72.9 |
| 10 | Top Esports | 2359.4 | 71.2 |
| 11 | Suning | 2355.4 | 69.8 |
| 12 | Fnatic | 2350.8 | 70.5 |
| 13 | Team Liquid | 2344.2 | 70.4 |
| 14 | Cloud9 | 2334.0 | 71.1 |
| 15 | Gen.G | 2330.1 | 69.0 |
| 16 | Nongshim RedForce | 2326.8 | 67.8 |
| 17 | Bilibili Gaming | 2319.5 | 73.6 |
| 18 | G2 Esports | 2313.9 | 79.1 |
| 19 | 100 Thieves | 2313.1 | 76.9 |
| 20 | Afreeca Freecs | 2306.5 | 67.7 |
| 21 | TSM | 2290.5 | 69.9 |
| 22 | Rogue (European Team) | 2288.2 | 80.1 |
| 23 | Liiv SANDBOX | 2286.0 | 69.4 |
| 24 | Misfits Gaming | 2283.4 | 77.4 |
| 25 | Evil Geniuses.NA | 2263.6 | 72.2 |
| 26 | Hanwha Life Esports | 2253.5 | 72.7 |
| 27 | KT Rolster | 2248.1 | 69.8 |
| 28 | JD Gaming | 2247.9 | 75.8 |
| 29 | Oh My God | 2225.6 | 76.1 |
| 30 | Fredit BRION | 2214.0 | 70.4 |
| 31 | Invictus Gaming | 2213.7 | 74.1 |
| 32 | LGD Gaming | 2200.8 | 77.6 |
| 33 | Rogue Warriors | 2193.0 | 80.6 |
| 34 | Immortals | 2186.4 | 78.1 |
| 35 | Team Vitality | 2170.9 | 85.7 |
| 36 | Excel Esports | 2151.8 | 91.9 |
| 37 | Astralis | 2140.0 | 90.9 |
| 38 | Ultra Prime | 2137.5 | 78.0 |
| 39 | Dignitas | 2118.6 | 75.6 |
| 40 | SK Gaming | 2094.7 | 93.9 |
| 41 | DRX | 2082.8 | 75.2 |
| 42 | Golden Guardians | 2078.0 | 85.7 |
| 43 | ThunderTalk Gaming | 2071.6 | 77.9 |
| 44 | FlyQuest | 2043.1 | 82.8 |
| 45 | FC Schalke 04 Esports | 2036.2 | 89.9 |
| 46 | Counter Logic Gaming | 2005.7 | 86.6 |
| 47 | Victory Five | 1944.6 | 86.8 |

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
