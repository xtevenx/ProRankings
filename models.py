import datetime
import time

import glicko2_utils

_DEVIATION_RESET_DAYS: float = 365.2425


def convert_to_days(str_: str) -> float:
    dt = datetime.datetime.strptime(str_, "%Y-%m-%d %H:%M:%S")
    return dt.timestamp() / 60 / 60 / 24


class TeamData:

    def __init__(self, name: str, creation_date: str) -> None:
        self.name: str = name
        self.rating: float = glicko2_utils.INITIAL_RATING
        self.deviation: float = glicko2_utils.INITIAL_DEVIATION
        self.volatility: float = glicko2_utils.INITIAL_VOLATILITY

        # Format: [(date: str, rating: float), ... ]
        self.rating_history: list = [(creation_date, self.rating)]

        # In number of days after the Unix epoch.
        self._last_game: float = convert_to_days(creation_date)

    def update_rating(self, opponent: "TeamData", score: float,
                      date: str) -> None:
        date_days = convert_to_days(date)
        new_stats = glicko2_utils.update_stats(
            rating=self.rating,
            deviation=self.deviation,
            volatility=self.volatility,
            results=((opponent.rating, opponent.deviation, score), ),
            time=date_days - self._last_game)

        self.rating, self.deviation, self.volatility = new_stats
        self.rating_history.append((date, self.rating))
        self._last_game = date_days

    def soft_reset_stats(self) -> None:
        self.deviation = glicko2_utils.update_deviation(
            self.deviation, self.volatility, time=_DEVIATION_RESET_DAYS)


class QueryDelay:

    def __init__(self, minimum_delay: float) -> None:
        self._delay: float = minimum_delay
        self.last_query: float = time.perf_counter() - self._delay

    def ensure_delay(self) -> None:
        while time.perf_counter() < self.last_query + self._delay:
            ...
        self.last_query = time.perf_counter()
