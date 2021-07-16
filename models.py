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

        # In number of days after the Unix epoch.
        self._last_game: float = convert_to_days(creation_date)

        # Format: [(date: str, rating: float), ... ]
        self.rating_history: list = [(creation_date, self.rating)]

    def update_rating(self, opponent: "TeamData", score: float, date: str) -> None:
        self.rating, self.deviation, self.volatility = glicko2_utils.update_stats(
            rating=self.rating,
            deviation=self.deviation,
            volatility=self.volatility,
            results=((opponent.rating, opponent.deviation, score),),
            # By the way, this next line is horrible code design because
            # `date_days` is defined in a very nondescript manner yet is used
            # later and not in the same "code block". The # only reason it is
            # defined here is because... idk it didn't look good defining it
            # before lol.
            time=(date_days := convert_to_days(date)) - self._last_game
        )

        self._last_game = date_days

    def soft_reset_stats(self) -> None:
        self.deviation = glicko2_utils.update_deviation(
            self.deviation, self.volatility, time=_DEVIATION_RESET_DAYS
        )


class QueryDelay:
    def __init__(self, minimum_delay: float) -> None:
        self._delay: float = minimum_delay
        self.last_query: float = time.time() - self._delay

    def ensure_delay(self) -> None:
        while time.time() < self.last_query + self._delay:
            ...
        self.last_query = time.time()
