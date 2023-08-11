import requests
import logging

from .auth import get_cookie
from config import *


# Конфигурация
config = PersonalConfig

# Логирование
logging.basicConfig(
    level=logging.INFO,
    filename="/usr/lib/zabbix/alertscripts/logs/zapi.log",
    format=config.FORMAT,
)


def get_graph(settings: dict, config: object) -> tuple[bytes, str, int]:
    """Функция получения графика по запросу к Zabbix.

    Args:
        settings (dict): Настройки из шаблона Zabbix
        config (object): Конфигурация скрипта

    Returns:
        tuple[bytes, str, int]:
            - content (bytes): График
            - url (str): Ссылка на график
            - status code (int): Код статуса запроса
    """

    url = f"{config.zabbix_api_url}chart.php?"
    params = {
        "from": f"now-{config.period}",
        "to": "now",
        "width": f"{config.graph_width}",
        "height": f"{config.graph_height}",
        "itemids[0]": f"{settings['itemid']}",
        "profileIdx": "web.item.graph.filter",
        "legend": "1",
        "showtriggers": "1",
        "showworkperiod": "1",
    }
    cookies = get_cookie(config)

    response = requests.get(
        url,
        params,
        cookies=cookies,
        verify=False,
    )

    # logging.info(f"{response.url}")

    return response.content, response.url, response.status_code
