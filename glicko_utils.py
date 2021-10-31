"""glicko_utils.py

This module contains a function for calculating ratings based on the Glicko
rating system (described here: http://www.glicko.net/glicko/glicko.pdf).
"""

import math
from typing import Sequence, Tuple

# The `Result` type represents the result of a game. It is a tuple of three
# values which represent the opponent's rating, opponent's rating deviation,
# and match score (0 <= x <= 1) respectively.
Result = Tuple[float, float, float]

# The `ResultList` type represents a collection of match results.
ResultList = Sequence[Result]

# Set various Glicko rating system variables.
INITIAL_RATING: float = 1500
INITIAL_DEVIATION: float = 350

TYPICAL_DEVIATION: float = 50
TIME_TO_UNRATED: float = 2 * 365.2425

# Calculate various Glicko rating system variables.
C: float = math.sqrt((INITIAL_DEVIATION ** 2 - TYPICAL_DEVIATION ** 2) / TIME_TO_UNRATED)
Q: float = math.log(10) / 400


# Private helper functions.
def _rd(rd: float, t: float = 1.0) -> float:
    """Step 1 of the Glicko rating system."""
    return min(math.sqrt(rd ** 2 + C ** 2 * t), INITIAL_DEVIATION)


def _g(rd: float) -> float:
    return 1 / math.sqrt(1 + 3 * (Q ** 2) * (rd ** 2) / (math.pi ** 2))


def _e(r: float, enemy_r: float, enemy_rd: float) -> float:
    return 1 / (1 + 10 ** (-_g(enemy_rd) * (r - enemy_r) / 400))


def _d(r: float, tournament_scores: ResultList) -> float:
    temp = 0
    for enemy_r, enemy_rd, _ in tournament_scores:
        e = _e(r, enemy_r, enemy_rd)
        temp += (_g(enemy_rd) ** 2) * e * (1 - e)
    d_squared = 1 / ((Q ** 2) * temp)
    return math.sqrt(d_squared)


def _new_r(r: float, rd: float, tournament_scores: ResultList) -> (float, float):
    rd = _rd(rd)

    temp = 0
    for enemy_r, enemy_rd, s in tournament_scores:
        temp += _g(enemy_rd) * (s - _e(r, enemy_r, enemy_rd))
    d = _d(r, tournament_scores)

    diff = Q / (1 / (rd ** 2) + 1 / (d ** 2)) * temp
    return r + diff, d


def _new_rd(rd: float, d: float) -> float:
    return math.sqrt(1 / (1 / (rd ** 2) + 1 / (d ** 2)))


# Public functions.
def update_stats(rating: float, deviation: float, results: ResultList,
                 time: float = 1.) -> (float, float):
    """Get new stats for a player based on a collection of games.

    Calculate a new rating and rating deviation for a player based on
    their record of game results with other players.

    :param float rating: the current rating of the player.
    :param float deviation: the current rating deviation of the player.
    :param ResultList results: The collection of game results with which to
        calculate the new stats.
    :param float time: The amount of time that has passed since the stats were
        last updated. This value is in an arbitrary unit determined by the
        rating system manager.

    :return tuple: Two values representing the player's new rating and rating
        deviation respectively.
    """

    deviation = update_deviation(deviation, time=time)
    if not results:
        return rating, deviation

    rating, d = _new_r(rating, deviation, results)
    deviation = _new_rd(deviation, d)
    return rating, deviation


def update_deviation(deviation: float, time: float = 1.) -> float:
    """Update a rating deviation."""
    return _rd(deviation, time)


if __name__ == "__main__":
    print(update_stats(rating=1500, deviation=200,
                       results=((1400, 30, 1), (1550, 100, 0), (1700, 300, 0))))
