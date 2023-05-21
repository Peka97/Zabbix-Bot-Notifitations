from config import BaseConfig

config = BaseConfig


def is_admin(user_id: int | str):
    return int(user_id) in config.ADMINS
