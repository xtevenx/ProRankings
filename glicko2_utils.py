"""
file: glicko2_utils.py

description: this module contains various utility functions for
calculating ratings based on the glicko-2 rating system.

ref: http://www.glicko.net/glicko/glicko2.pdf
"""

import math
from typing import Sequence, Tuple

# type definitions
MATCH_RESULT = Tuple[float, float, float]
ALL_MATCH_RESULTS = Sequence[MATCH_RESULT]

# glicko rating utility definitions
INITIAL_RATING: float = 1649
INITIAL_DEVIATION: float = 350
INITIAL_VOLATILITY: float = 0.06

TAU: float = 1.2


# helper functions
def _convert_v1(r: float, rd: float) -> (float, float):
    return 173.7178 * r + 1500, 173.7178 * rd


def _convert_v2(r: float, rd: float) -> (float, float):
    return (r - 1500) / 173.7178, rd / 173.7178


def _g(phi: float) -> float:
    return 1 / math.sqrt(1 + (3 * phi ** 2) / (math.pi ** 2))


def _e(mu: float, mu_j: float, phi_j: float) -> float:
    return 1 / (1 + math.exp(-_g(phi_j) * (mu - mu_j)))


def _get_v(mu: float, results: ALL_MATCH_RESULTS) -> float:
    v_inv = 0
    for mu_j, phi_j, _ in results:
        x = _e(mu, mu_j, phi_j)
        v_inv += (_g(phi_j) ** 2) * x * (1 - x)
    return 1 / v_inv


def _get_delta(mu: float, results: ALL_MATCH_RESULTS) -> float:
    delta = 0
    for mu_j, phi_j, s_j in results:
        delta += _g(phi_j) * (s_j - _e(mu, mu_j, phi_j))
    return _get_v(mu, results) * delta


def _get_sigma_p(mu: float, phi: float, sigma: float, results: ALL_MATCH_RESULTS) -> float:
    v = _get_v(mu, results)
    delta = _get_delta(mu, results)

    # step 1
    a = math.log(sigma ** 2)
    epsilon = 0.000001

    def f(x):
        l1 = (math.e ** x) * (delta ** 2 - phi ** 2 - v - math.e ** x)
        l2 = 2 * (phi ** 2 + v + math.e ** x) ** 2
        r = (x - a) / TAU ** 2
        return l1 / l2 - r

    # step 2
    big_a = a
    if delta ** 2 > phi ** 2 + v:
        big_b = math.log(delta ** 2 - phi ** 2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k += 1
        big_b = a - k * TAU

    # step 3
    f_a = f(big_a)
    f_b = f(big_b)

    # step 4
    while abs(big_b - big_a) > epsilon:
        big_c = big_a + (big_a - big_b) * f_a / (f_b - f_a)
        f_c = f(big_c)

        if f_c * f_b < 0:
            big_a = big_b
            f_a = f_b
        else:
            f_a = f_a / 2

        big_b = big_c
        f_b = f_c

    # step 5
    return math.e ** (big_a / 2)


# public functions
def get_new_stats(rating: float,
                  deviation: float,
                  volatility: float,
                  results: ALL_MATCH_RESULTS) -> (float, float, float):
    """
    Calculate a new rating and rating deviation for a player based on
    their record of game results with other players (`tournament_scores`).

    :param float rating: the current rating of the player.
    :param float deviation: the current rating deviation of the player.
    :param float volatility: the current rating volatility of the player.
    :param tuple results: a tuple of game results with each result being
        a tuple consisting of:
          * `float`: the opponent's rating,
          * `float`: the opponent's rating deviation,
          * `float`: the score against this opponent as a percentage (0 <= x <= 1)

    :return tuple: a triple of numbers containing the player's new rating,
        rating deviation and rating volatility.
    """

    rating, deviation = _convert_v2(rating, deviation)

    v2_results = []
    for r, rd, s in results:
        r, rd = _convert_v2(r, rd)
        v2_results.append((r, rd, s))

    sigma_p = _get_sigma_p(rating, deviation, volatility, v2_results)
    phi_a = math.sqrt(deviation ** 2 + sigma_p ** 2)

    phi_p = 1 / math.sqrt(1 / phi_a ** 2 + 1 / _get_v(rating, v2_results))

    mu_p = 0
    for mu_j, phi_j, s_j in v2_results:
        mu_p += _g(phi_j) * (s_j - _e(rating, mu_j, phi_j))
    mu_p = rating + phi_p ** 2 * mu_p

    rating, deviation = _convert_v1(mu_p, phi_p)
    volatility = sigma_p

    return rating, deviation, volatility


def update_deviation(deviation: float, volatility: float, time: float) -> float:
    """
    Calculate a new rating deviation based on the current deviation and
    how much time has passed since the last calculation.

    :param float deviation: the current rating deviation.
    :param float volatility: the current rating volatility.
    :param float time: the time since last rating calculation.
    :return float: the new rating deviation.
    """

    deviation = _convert_v2(0, deviation)[1]

    for _ in range(math.floor(time)):
        deviation = math.sqrt(deviation ** 2 + volatility ** 2)

    return _convert_v1(0, deviation)[1]
