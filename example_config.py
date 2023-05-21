class BaseConfig:
    ADMINS = [int, int]
    CHAT_ID = int
    THREAD_IDS = {"channel_name": "thread_id"}
    FORMAT = "%(asctime)-15s [%(levelname)s] (%(filename)s).%(funcName)s(%(lineno)d) %(message)s"
    API_TOKEN = "API_TOKEN_HERE"
    zabbix_api_login = "login"
    zabbix_api_pass = "password"
    zabbix_api_url = "http://YOUR_IP/zabbix/"
    period = "43200"
