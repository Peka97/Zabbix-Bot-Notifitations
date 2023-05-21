import requests

from .auth import get_cookie

# from py-zabbix import ZabbixAPI


class BaseConfig:
    ADMINS = [1387411715]
    CHAT_ID = -1001743552948
    THREAD_IDS = {
        "МБН": 2,
        "МЖБН": 12,
        "СХБН": 39,
        "СБН": 272,
        "ГК": 274,
    }
    FORMAT = "%(asctime)-15s [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) %(message)s"
    API_TOKEN = "5858306484:AAFIy5qgan4tfZWE6x9YAtROQArQGIqhNNU"
    zabbix_api_login = "zabbixbot"
    zabbix_api_pass = "sexbot666"
    zabbix_api_url = "http://130.193.42.73/zabbix/"
    period = "43200"


config = BaseConfig


def confirm_problem(settings, user):
    event_id = settings["eventid"]
    response = requests.post(
        url=f"{config.zabbix_api_url}api_jsonrpc.php",
        headers={"Content-Type": "application/json-rpc"},
        json={
            "jsonrpc": "2.0",
            "method": "event.acknowledge",
            "params": {
                "eventids": event_id,
                "action": 6,
                "message": f"Problem confirm by {user.last_name} {user.first_name}",
            },
        },
        cookies=get_cookie(config),
    )
    return response.content, response.url, response.status_code
