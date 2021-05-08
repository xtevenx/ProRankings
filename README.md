This site displays calculated ratings for professional League of Legends teams.
Only teams from the four major regions are included in the below charts, however
all games are accounted for when calculating the ratings. Due to the nature of
the rating system (see notes below), the ratings may be very inaccurate at the
start of each season, and generally become more accurate as more games are
played.

View the source on [GitHub][2].

Ratings of Teams at MSI 2021
----------------------------

This chart displays the ratings of teams at the Mid-Season Invitational of 2021.
Since MSI is the first international competition of the season, ratings at the
start of the tournament will be based heavily on a team's dominance within their
region, so teams from minor regions may have their ratings inflated.

![image missing](https://raw.githubusercontent.com/xtevenx/ProRankings/master/data/output_tourney.png "Ratings of Teams at MSI 2021")

Ratings of Top Teams
--------------------

This chart displays the calculated ratings for the top teams in the four major
leagues ([LCS][3], [LEC][4], [LCK][5], [LPL][6]).

[comment]: <> (Note: the top teams from minor leagues may have their ratings inflated if they )
[comment]: <> (dominated their league. This is because if there are no inter-region games, )
[comment]: <> (one's rating is solely based on their performance within their region.)

![image missing](https://raw.githubusercontent.com/xtevenx/ProRankings/master/data/output_bar.png "Ratings of Top Teams")

Rating Progression of Select Teams
----------------------------------

This chart displays the calculated rating progression for select teams.
![image missing](https://raw.githubusercontent.com/xtevenx/ProRankings/master/data/output_line.png "Rating Progression of Select Teams")

About the Rating System
-----------------------

The ratings are calculated using the [Glicko-2][1] rating system on weekly
intervals.

However, there are some things of note:

*   Each game in Mid-Season Invitationals or World Championships count for
    twice as much as other games.
*   At the start of each season, the ratings are reset approximately 40%
    towards the average, and the rating deviations are adjusted to be
    equivalent to if there was a year without play. This is done to try to
    account for the rapidly changing meta.
*   The average rating is set to the average FIDE standard rating which is, as
    of April 2021, 1647. There is no meaning behind this and is done purely based
    on personal preference.

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
