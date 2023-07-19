################################################################################
#                                                                              #
#        Данный файл является тестовым скриптом для разработки бота.           #
#                 Не рекомендуется для использования.                          #
#                                                                              #
################################################################################

from pprint import pprint

from pyzabbix import ZabbixAPI

from config import PersonalConfig as cfg


def get_all():
    zapi = ZabbixAPI(
        cfg.zabbix_api_url, user=cfg.zabbix_api_login, password=cfg.zabbix_api_pass
    )
    # zapi.login()
    print("Connected to Zabbix API Version %s" % zapi.api_version())

    # Get all monitored hosts
    hosts = zapi.host.get(monitored_hosts=1, output="extend")
    for host in hosts:
        pprint(host)


if __name__ == "__main__":
    get_all()
