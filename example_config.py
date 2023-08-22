################################################################################
#                                                                              #
#      Данный файл является примером конфигурации для настройки скрипта        #
#                                                                              #
################################################################################


class BaseConfig:
    """Объект с базовой конфигурацией скрипта"""

    # IDs from Aiogram (ты можешь использовать скрипт /utils/get_thread_id.py чтобы узнать свой ID, Chat ID и Thread ID)
    ADMINS = [
        "{USER_ID: int}",
        "{USER_ID: int}",
    ]

    # Logging format
    FORMAT = "%(asctime)-15s [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) %(message)s"

    # Token from BotFather
    API_TOKEN = "{API_TOKEN_HERE}"

    # Zabbix settings
    zabbix_api_login = "{LOGIN_HERE}"
    zabbix_api_pass = "{PASSWORD_HERE}"
    zabbix_api_url = "http://{YOUR_IP_HERE}/zabbix/"
    period = "43200"


class ChannelConfig(BaseConfig):
    """Конфигурация для рассылки в каналы супергруппы Telegram

    Args:
        BaseConfig (object): Базовая конфигурация
    """

    # IDs from Aiogram (ты можешь использовать скрипт /utils/get_thread_id.py чтобы узнать свой ID, Chat ID и Thread ID)
    CHAT_ID = "{CHAT_ID: int}"
    THREAD_IDS = {"{CHANNEL_NAME: str}": "{THREAD_ID: int}"}


class PersonalConfig(BaseConfig):
    """Конфигурация для персональной рассылки пользователям Telegram

    Args:
        BaseConfig (object): Базовая конфигурация
    """

    pass
