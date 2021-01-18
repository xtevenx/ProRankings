"""
file: glicko_utils.py

description: this module contains various utility functions for
calculating ratings based on the glicko rating system.

ref: http://www.glicko.net/glicko/glicko.pdf
"""

import math
from typing import Sequence, Tuple

# type definitions
MATCH_RESULT = Tuple[float, float, float]
ALL_MATCHES_RESULT = Sequence[MATCH_RESULT]

# glicko rating utility definitions
INITIAL_RATING: float = 1649
INITIAL_DEVIATION: float = 350

UNRATED_DEVIATION: float = 350
TYPICAL_DEVIATION: float = 50

# TIME_TO_UNRATED: float = 4.8 * 365.2425
TIME_TO_UNRATED: float = (21.2 - 13) * 365.2425

C: float = math.sqrt((UNRATED_DEVIATION ** 2 - TYPICAL_DEVIATION ** 2) / TIME_TO_UNRATED)
Q: float = math.log(10) / 400


# helper functions
def _get_rd(rd: float, t: float = 1.0) -> float:
    return min(math.sqrt(rd ** 2 + C ** 2 * t), UNRATED_DEVIATION)


def _get_g(rd: float) -> float:
    return 1 / math.sqrt(1 + 3 * (Q ** 2) * (rd ** 2) / (math.pi ** 2))


def _get_e(r: float, enemy_r: float, enemy_rd: float) -> float:
    return 1 / (1 + 10 ** (_get_g(enemy_rd) * (r - enemy_r) / (-400)))


def _get_d(r: float, tournament_scores: ALL_MATCHES_RESULT) -> float:
    temp = 0
    for enemy_r, enemy_rd, _ in tournament_scores:
        e = _get_e(r, enemy_r, enemy_rd)
        temp += (_get_g(enemy_rd) ** 2) * e * (1 - e)
    d_squared = 1 / ((Q ** 2) * temp)
    return math.sqrt(d_squared)


def _get_new_rating(r: float, rd: float, tournament_scores: ALL_MATCHES_RESULT) -> (float, float):
    rd = _get_rd(rd)

    temp = 0
    for enemy_r, enemy_rd, s in tournament_scores:
        temp += _get_g(enemy_rd) * (s - _get_e(r, enemy_r, enemy_rd))
    d = _get_d(r, tournament_scores)

    diff = Q / (1 / (rd ** 2) + 1 / (d ** 2)) * temp
    return r + diff, d


def _get_new_rd(rd: float, d: float) -> float:
    return math.sqrt(1 / (1 / (rd ** 2) + 1 / (d ** 2)))


# public functions
def get_new_stats(r: float, rd: float, tournament_scores: ALL_MATCHES_RESULT) -> (float, float):
    """
    Calculate a new rating and rating deviation for a player based on
    their record of game results with other players (`tournament_scores`).

    :param float r: the current rating of the player.
    :param float rd: the current rating deviation of the player.
    :param tuple tournament_scores: a tuple of game results with each result
        being a tuple consisting of:
          * `float`: the opponent's rating,
          * `float`: the opponent's rating deviation,
          * `float`: the score against this opponent as a percentage (0 <= x <= 1)

    :return tuple: a pair of numbers containing the player's new rating and
        rating deviation.
    """

    new_r, d = _get_new_rating(r, rd, tournament_scores)
    new_rd = _get_new_rd(rd, d)
    return new_r, new_rd


def update_deviation(rd: float, t: float) -> float:
    """
    Calculate a new rating deviation based on the current deviation and
    how much time has passed since the last calculation.

    :param float rd: the current rating deviation.
    :param float t: the time since last rating calculation.
    :return float: the new rating deviation.
    """

    return _get_rd(rd, t)
