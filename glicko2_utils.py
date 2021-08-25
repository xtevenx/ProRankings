"""glicko2_utils.py

This module contains a function for calculating ratings based on the Glicko-2
rating system (described here: http://www.glicko.net/glicko/glicko2.pdf).
"""

import math
from typing import Sequence, Tuple

# The `Result` type represents the result of a game. It is a tuple of three
# values which represent the opponent's rating, opponent's rating deviation,
# and match score (0 <= x <= 1) respectively.
Result = Tuple[float, float, float]

# The `ResultList` type represents a collection of match results.
ResultList = Sequence[Result]

# Set various Glicko-2 rating system variables.
INITIAL_RATING: float = 1645.15
INITIAL_DEVIATION: float = 350
INITIAL_VOLATILITY: float = 0.06

TAU: float = 1.2


# Private helper functions.
def _convert_v1(mu: float, phi: float) -> (float, float):
    """Convert a Glicko-2 scale rating/deviation pair to Glicko-1."""
    return 173.7178 * mu + 1500, 173.7178 * phi


def _convert_v2(r: float, rd: float) -> (float, float):
    """Convert a Glicko-1 scale rating/deviation pair to Glicko-2."""
    return (r - 1500) / 173.7178, rd / 173.7178


def _g(phi: float) -> float:
    # return 1 / math.sqrt(1 + (3 * phi ** 2) / (math.pi ** 2))
    return 1 / math.sqrt(1 + 3 * (phi / math.pi) ** 2)


def _e(mu: float, mu_j: float, phi_j: float) -> float:
    return 1 / (1 + math.exp(-_g(phi_j) * (mu - mu_j)))


def _get_v(mu: float, results: ResultList) -> float:
    """Step 3 of the Glicko-2 rating system.

    The ratings and rating deviations in `results` should all be in the Glicko-2
    rating system's scale.
    """

    v_inv = 0
    for mu_j, phi_j, _ in results:
        x = _e(mu, mu_j, phi_j)
        v_inv += (_g(phi_j) ** 2) * x * (1 - x)
    return 1 / v_inv


def _get_delta(mu: float, results: ResultList) -> float:
    """Step 4 of the Glicko-2 rating system.

    The ratings and rating deviations in `results` should all be in the Glicko-2
    rating system's scale.
    """

    delta = 0
    for mu_j, phi_j, s_j in results:
        delta += _g(phi_j) * (s_j - _e(mu, mu_j, phi_j))
    return _get_v(mu, results) * delta


def _get_sigma_p(mu: float, phi: float, sigma: float, results: ResultList) -> float:
    """Step 5 of the Glicko-2 rating system.

    The ratings and rating deviations in `results` should all be in the Glicko-2
    rating system's scale.
    """

    # Part 0
    v = _get_v(mu, results)
    delta = _get_delta(mu, results)

    # Part 1
    a = math.log(sigma ** 2)
    epsilon = 0.000001

    def f(x):
        l1 = math.exp(x) * (delta ** 2 - phi ** 2 - v - math.exp(x))
        l2 = 2 * (phi ** 2 + v + math.exp(x)) ** 2
        r = (x - a) / TAU ** 2
        return l1 / l2 - r

    # Part 2
    big_a = a
    if delta ** 2 > phi ** 2 + v:
        big_b = math.log(delta ** 2 - phi ** 2 - v)
    else:
        k = 1
        while f(a - k * TAU) < 0:
            k = k + 1
        big_b = a - k * TAU

    # Part 3
    f_a = f(big_a)
    f_b = f(big_b)

    # Part 4
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

    # Part 5
    return math.exp(big_a / 2)


# Public functions.
def update_stats(rating: float, deviation: float, volatility: float, results: ResultList,
                 time: float = 1) -> (float, float, float):
    """Get new stats for a player based on a collection of games.

    Calculate a new rating, deviation, and volatility for a player based on
    a record of their game results with other players.

    The ratings and rating deviations used as arguments to this function are
    all in the Glicko-1 rating system's scale.

    :param float rating: The current rating of the player.
    :param float deviation: The current rating deviation of the player.
    :param float volatility: The current rating volatility of the player.
    :param ResultList results: The collection of game results with which to
        calculate the new stats.
    :param float time: The amount of time that has passed since the stats were
        last updated. This value is in an arbitrary unit determined by the
        rating system manager.

    :return tuple: Three values representing the player's new rating,
        deviation and volatility respectively.
    """

    if not results:
        deviation = update_deviation(deviation, volatility, time=time)
        return rating, deviation, volatility

    # Step 0
    mu, phi = _convert_v2(rating, deviation)
    sigma = volatility

    v2_results = []
    for r, rd, s in results:
        _mu, _phi = _convert_v2(r, rd)
        v2_results.append((_mu, _phi, s))

    # Steps 1-5
    sigma_p = _get_sigma_p(mu, phi, sigma, v2_results)

    # Step 6
    phi_s = math.sqrt(phi ** 2 + time * sigma_p ** 2)

    # Step 7
    phi_p = 1 / math.sqrt(1 / phi_s ** 2 + 1 / _get_v(mu, v2_results))

    mu_p = 0
    for mu_j, phi_j, s_j in v2_results:
        mu_p += _g(phi_j) * (s_j - _e(mu, mu_j, phi_j))
    mu_p = mu + phi_p ** 2 * mu_p

    # Step 8
    rating, deviation = _convert_v1(mu_p, phi_p)
    volatility = sigma_p

    return rating, deviation, volatility


def update_deviation(deviation: float, volatility: float, time: float = 1) -> float:
    """Update a rating deviation."""
    _, phi = _convert_v2(float(), deviation)
    phi = math.sqrt(phi ** 2 + time * volatility ** 2)
    _, deviation = _convert_v1(float(), phi)
    return deviation


def win_pct(rating_1: float, deviation_1: float, rating_2: float, deviation_2: float) -> float:
    """Get the estimated win percentage for a match-up.

    Calculates the estimated win percentage for Player 1 in their match-up
    against Player 2 given both of their stats.

    The ratings and rating deviations used as arguments to this function are
    all in the Glicko-1 rating system's scale.

    :param float rating_1: The rating of Player 1.
    :param float deviation_1: The rating deviation of Player 1.
    :param float rating_2: The rating of Player 2.
    :param float deviation_2: The rating deviation of Player 2.

    :return float: A fraction between zero and one representing the estimated
        win percentage.
    """

    mu_1, phi_1 = _convert_v2(rating_1, deviation_1)
    mu_2, phi_2 = _convert_v2(rating_2, deviation_2)

    return _e(mu_1, mu_2, math.sqrt(phi_1 ** 2 + phi_2 ** 2))


if __name__ == "__main__":
    TAU: float = 0.5

    print(update_stats(rating=1500, deviation=200, volatility=0.06,
                       results=((1400, 30, 1), (1550, 100, 0), (1700, 300, 0))))

    print(win_pct(1500, 200, 1400, 30))
    print(win_pct(1500, 200, 1550, 100))
    print(win_pct(1500, 200, 1700, 300))
