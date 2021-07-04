import time
import glicko2_utils

_RATING_INTERVAL = 7
_DAYS_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

_RATING_RESET_FACTOR: int = 32

# Time in _RATING_INTERVAL units to artificially adjust the rating
# deviation by, every new season. Currently set to one year.
_DEVIATION_RESET_TIME: int = 365 // _RATING_INTERVAL


def convert_to_days(utc_string: str) -> int:
    # remove the time of day from the date and time.
    utc_string = utc_string.split()[0]

    # calculate the amount of days since year zero.
    year, month, day = [int(n) for n in utc_string.split("-")]

    days = 365 * year
    days += (year % 400 == 0) or (year % 4 == 0 and year % 100 != 0)
    days += sum(_DAYS_PER_MONTH[:month - 1])
    days += (month > 2) and (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0))
    days += day

    return days


class TeamData:
    def __init__(self, name: str, creation_date: str):
        self.name: str = name
        self.last_game: int = convert_to_days(creation_date)

        self.rating: float = glicko2_utils.INITIAL_RATING
        self.deviation: float = glicko2_utils.INITIAL_DEVIATION
        self.volatility: float = glicko2_utils.INITIAL_VOLATILITY

        # [(date, rating), (date, rating), ... ]
        self.rating_history: list = [(creation_date, self.rating)]

        # [(rating, deviation, win_loss), ... ]
        self.games_bank: list = []
        self.games_bank_end: int = 0

    def update_rating(self, opponent: "TeamData", win_loss: float, date: str):
        date_number = convert_to_days(date)
        if self.games_bank_end == 0:
            self.games_bank_end = date_number + _RATING_INTERVAL

        if date_number >= self.games_bank_end:
            self.finalize(date)

        self.games_bank.append((opponent.rating, opponent.deviation, win_loss))
        self.last_game = date_number

    def finalize(self, date):
        if self.games_bank:
            self.rating, self.deviation, self.volatility = glicko2_utils.get_new_stats(
                self.rating, self.deviation, self.volatility, self.games_bank)
            self.rating_history.append((date, self.rating))

        self.games_bank.clear()

        new_bank_end = convert_to_days(date) + _RATING_INTERVAL
        self.deviation = glicko2_utils.update_deviation(
            self.deviation, self.volatility,
            (new_bank_end - self.games_bank_end) // _RATING_INTERVAL - 1
        )
        self.games_bank_end = new_bank_end

    def soft_reset_stats(self):
        self.rating, self.deviation, self.volatility = glicko2_utils.get_new_stats(
            self.rating, self.deviation, self.volatility,
            ((glicko2_utils.INITIAL_RATING, glicko2_utils.INITIAL_DEVIATION, 0.5),) * _RATING_RESET_FACTOR
        )
        self.deviation = glicko2_utils.update_deviation(
            self.deviation, self.volatility, _DEVIATION_RESET_TIME - 1
        )


class QueryDelay:
    def __init__(self, minimum_delay: float) -> None:
        self._delay: float = minimum_delay
        self.last_query: float = time.time() - self._delay

    def ensure_delay(self) -> None:
        while time.time() < self.last_query + self._delay:
            ...
        self.last_query = time.time()
