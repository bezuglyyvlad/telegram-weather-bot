import config
from vedis import Vedis


def get_value(db_file, user_id):
    with Vedis(db_file) as db:
        try:
            return db[user_id].decode()
        except KeyError:
            return config.States.S_START.value


def set_value(db_file, user_id, value):
    with Vedis(db_file) as db:
        try:
            db[user_id] = value
            return True
        finally:
            return False
