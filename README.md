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

This table contains rating data for all major region teams.

| | Team | Rating | Deviation |
| --: | --- | :-: | :-: |
| 1 | FunPlus Phoenix | 2546 | 78.41 |
| 2 | DWG KIA | 2528 | 74.98 |
| 3 | MAD Lions | 2507 | 80.18 |
| 4 | Royal Never Give Up | 2460 | 74.47 |
| 5 | EDward Gaming | 2456 | 79.22 |
| 6 | Team WE | 2416 | 66.50 |
| 7 | LNG Esports | 2376 | 63.61 |
| 8 | Gen.G | 2368 | 73.13 |
| 9 | T1 | 2363 | 72.03 |
| 10 | Rare Atom | 2362 | 72.85 |
| 11 | Top Esports | 2359 | 71.18 |
| 12 | Suning | 2355 | 69.83 |
| 13 | G2 Esports | 2346 | 85.60 |
| 14 | Rogue (European Team) | 2344 | 82.47 |
| 15 | Team Liquid | 2344 | 70.41 |
| 16 | Cloud9 | 2342 | 73.10 |
| 17 | Nongshim RedForce | 2327 | 67.83 |
| 18 | Bilibili Gaming | 2319 | 73.55 |
| 19 | Afreeca Freecs | 2306 | 67.72 |
| 20 | TSM | 2296 | 76.28 |
| 21 | 100 Thieves | 2294 | 73.86 |
| 22 | Liiv SANDBOX | 2286 | 69.37 |
| 23 | Misfits Gaming | 2283 | 77.37 |
| 24 | Fnatic | 2283 | 76.69 |
| 25 | Evil Geniuses.NA | 2264 | 72.18 |
| 26 | Hanwha Life Esports | 2254 | 72.70 |
| 27 | KT Rolster | 2248 | 69.80 |
| 28 | JD Gaming | 2248 | 75.78 |
| 29 | Oh My God | 2226 | 76.07 |
| 30 | Fredit BRION | 2214 | 70.40 |
| 31 | Invictus Gaming | 2214 | 74.13 |
| 32 | LGD Gaming | 2201 | 77.63 |
| 33 | Rogue Warriors | 2193 | 80.65 |
| 34 | Immortals | 2186 | 78.09 |
| 35 | Team Vitality | 2171 | 85.74 |
| 36 | Excel Esports | 2152 | 91.94 |
| 37 | Astralis | 2140 | 90.87 |
| 38 | Ultra Prime | 2137 | 77.95 |
| 39 | Dignitas | 2119 | 75.57 |
| 40 | SK Gaming | 2095 | 93.86 |
| 41 | DRX | 2083 | 75.25 |
| 42 | Golden Guardians | 2078 | 85.74 |
| 43 | ThunderTalk Gaming | 2072 | 77.91 |
| 44 | FlyQuest | 2043 | 82.82 |
| 45 | FC Schalke 04 Esports | 2036 | 89.87 |
| 46 | Counter Logic Gaming | 2006 | 86.58 |
| 47 | Victory Five | 1945 | 86.77 |

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
