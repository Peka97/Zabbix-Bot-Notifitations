from config import *
from utils.zapi.zapi import ZabbixAPI


config = BaseConfig()

zapi = ZabbixAPI(config.zabbix_api_url, config.zabbix_api_login, config.zabbix_api_pass)
