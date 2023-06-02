import requests

from .auth import get_cookie


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

    zabbix_graph_chart = (
        "{zabbix_server}chart3.php?"
        "name={name}&"
        "from=now-{range_time}&"
        "to=now&"
        "width=900&"
        "height=200&"
        "items[0][itemid]={itemid}&"
        "legend=1&"
        "showtriggers=1&"
        "showworkperiod=1"
    )

    response = requests.get(
        zabbix_graph_chart.format(
            name=settings["title"],
            itemid=settings["itemid"].split()[0],
            zabbix_server=config.zabbix_api_url,
            range_time=config.period,
        ),
        cookies=get_cookie(config),
        verify=False,
    )

    return response.content, response.url, response.status_code
