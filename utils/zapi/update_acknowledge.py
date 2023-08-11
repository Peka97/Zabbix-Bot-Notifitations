import requests
from aiogram.types import User

from .auth import get_cookie

from config import *

# from py-zabbix import ZabbixAPI

config = PersonalConfig


def confirm_problem(settings: dict, user: User) -> int:
    """Функция, подтверждающая проблему в Zabbix.

    Args:
        settings (dict): Словарь с параметрами для поиска триггера в Zabbix.
        user (User): Экземпляр пользователя Telegram.

    Returns:
        status code (int): Код статуса запроса
    """
    event_id = settings["eventid"]
    url = f"{config.zabbix_api_url}api_jsonrpc.php"
    json_ = {
        "jsonrpc": "2.0",
        "method": "event.acknowledge",
    }
    params = {
        "eventids": event_id,
        "action": 6,
        "message": f"Problem confirm by {user.last_name} {user.first_name}",
    }
    headers = {"Content-Type": "application/json-rpc"}

    response = requests.post(
        url=url,
        json=json_,
        params=params,
        headers=headers,
        cookies=get_cookie(config),
    )

    return response.status_code
