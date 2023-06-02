import requests


def get_cookie(config: object) -> None:
    """Запрос на сервер Zabbix для формирования cookie.

    Args:
        config (object): Конфигурация скрипта Zabbix

    Returns:
        None
    """

    data_api = {
        "name": config.zabbix_api_login,
        "password": config.zabbix_api_pass,
        "enter": "Sign in",
    }
    req_cookie = requests.post(config.zabbix_api_url, data=data_api, verify=False)
    cookie = req_cookie.cookies

    req_cookie.close()
    return cookie
