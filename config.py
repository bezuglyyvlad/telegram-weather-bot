from enum import Enum

DB_FILE_STATE = "stateDB.vdb"
DB_FILE_LOCATION = "locationDB.vdb"
DATE_FORMAT = "%A, %d %B"

W_TODAY_TITLE = "На сегодня"
W_TOMORROW_TITLE = "На завтра"
W_5_DAYS_TITLE = "На 5 дней"


class States(Enum):
    S_START = "0"
    S_ENTER_LOCATION = "1"
    S_WEATHER_TODAY = "2"
    S_WEATHER_TOMORROW = "3"
    S_WEATHER_NEXT_5_DAYS = "4"
