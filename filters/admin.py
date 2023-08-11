from config import BaseConfig

config = BaseConfig


def is_admin(user_id: int | str) -> bool:
    """Функция проверки ID пользователя:
        - если пользователь есть в конфигурации проекта, то вернёт True
        - если пользователя нет в конфигурации проекта, то вернёт False

    Args:
        user_id (int | str): ID пользователя в Telegram

    Returns:
        bool: True or False
    """
    return int(user_id) in config.ADMINS
