import glicko_utils

DAYS_PER_MONTH = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def convert_to_days(utc_string: str) -> int:
    # remove the time of day from the date and time.
    utc_string = utc_string.split()[0]

    # calculate the amount of days since year zero.
    year, month, day = [int(n) for n in utc_string.split("-")]

    days = 365 * year
    days += (year // 4) - (year // 100) + (year // 400)
    days += sum(DAYS_PER_MONTH[:month - 1])
    days += (month > 2) and (year % 400 == 0 or (year % 4 == 0 and year % 100 != 0))
    days += day

    return days


class TeamData:
    def __init__(self, name: str, creation_date: str):
        self.name: str = name
        self.last_game: int = convert_to_days(creation_date)

        self.rating: float = glicko_utils.INITIAL_RATING
        self.deviation: float = glicko_utils.INITIAL_DEVIATION

        # [(date, rating), (date, rating), ... ]
        self.rating_history: list = [(creation_date, self.rating)]

    def update_rating(self, opponent: "TeamData", win_loss: float, date: str):
        self.update_deviation(date)

        self.rating, self.deviation = glicko_utils.get_new_stats(
            self.rating,
            self.deviation,
            ((opponent.rating, opponent.deviation, win_loss),)
        )

        self.rating_history.append((date, self.rating))

    def update_deviation(self, date: str):
        game_date = convert_to_days(date)
        self.deviation = glicko_utils.update_deviation(self.deviation, game_date - self.last_game)
        self.last_game = game_date
