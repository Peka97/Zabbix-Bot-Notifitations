#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import logging
import requests
import json
from time import time
from pprint import pprint
from tabulate import tabulate

import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet
from aiogram.types import User

from .output import Output
from config import *
from .auth import get_cookie


logging.getLogger("zapi.log")
config = PersonalConfig


class ZabbixAPI:
    """Description
    ------
    Модель взаимодействия с API системы мониторинга Zabbix.
    Авторизация в системе проходит через специальный `token`, который можно
    получить после прохождения авторизации через `login` и `password`.

    Methods:
    ------
        * `get_host_interfaces`: Получение интерфейсов хоста через имя хоста;
        * `get_hosts_interfaces_by_group_id`: Получение интерфейсов хоста через ID группы;
        * `get_hosts_by_group_name`: Получение хостов через имя группы;
        * `get_group_id_by_group_name`: Получение ID группы через имя группы.
    """

    headers = {"Content-Type": "application/json"}
    output = Output()

    def __init__(self, url: str, login: str, password: str):
        """Description
        ------
        Создание и возврат экземпляра `ZabbixAPI`.
        Проходит авторизацию в API системы мониторинга Zabbix.

        Args:
        ------
            * `url` (str): URL сервера Zabbix в формате "http://127.0.0.1/zabbix/";
            * `login` (str): Логин в системе мониторинга Zabbix;
            * `password` (str): Пароль в системе мониторинга Zabbix.
        """

        self._url = f"{url}api_jsonrpc.php"
        self._login = login
        self._password = password
        self._auth(login, password)

    def _auth(self, login: str, password: str) -> None:
        """Description
        ------
        Авторизация в системе мониторинга Zabbix средствами API.

        После отправки `login` и `password` возвращается `token`, который
        используется в дальнейших обращениях к API.

        Args:
        ------
            * `login` (str): _description_
            * `password` (str): _description_

        Raises:
        ------
            * ValueError: Неверный логин или пароль
        """

        data = {
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "username": login,
                "password": password,
            },
            "id": 1,
        }

        # Запрашиваем токен
        res = requests.post(self._url, json.dumps(data), headers=self.headers)
        token = res.json().get("result")

        if token:
            # Сохраняем токен
            self._token = token

            # Запрашиваем и сохранем cookies
            data_api = {
                "name": login,
                "password": password,
                "enter": "Sign in",
            }
            res = requests.post(config.zabbix_api_url, data=data_api, verify=False)
            self._cookies = res.cookies
        else:
            raise ValueError("Неверное имя пользователя и/или пароль")

    def get_group_id_by_group_name(
        self, group_name: str | list[str]
    ) -> list[str] | None:
        """Description
        ------
        Получение ID группы  по имени группы.
        Устройство API позволяет передать массив ID и получить массив имён.

        Args:
        ------
            * `group_name` (str | list[str]): имя группы или массив имён групп.

        Returns:
        ------
            * list[str] | None: список ID групп, удовлетворающих критериям запроса.
        """

        data = {
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "filter": {"name": group_name},
                "output": [
                    # Возможные значения: ["groupid", "name", "flags", "uuid"]
                    "groupid",
                    "name",
                ],
            },
            "auth": self._token,
            "id": 1,
        }

        res = requests.get(self._url, data=json.dumps(data), headers=self.headers)
        result = res.json().get("result")
        try:
            group_ids = [field["groupid"] for field in result]

            if not group_ids:
                return

        except Exception as err:
            logging.error(err)
            return

        return group_ids

    def get_hosts_interfaces_by_group_id(
        self, group_ids: str | list[str]
    ) -> list[dict] | None:
        """Description
        ------
        Получение данных хостов с инвентаризацией через ID групп.
        Инвентаризация распаковывается за счёт метода `ZabbitAPI`.

        Args:
        ------
            * `group_ids` (str | list[str]): массив ID групп.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        if not group_ids:
            return

        result = []

        for group_id in group_ids:
            data = {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {"groupids": group_id},
                    "output": ["hostid", "host", "name"],
                    "selectInterfaces": ["ip", "port", "dns"],
                },
                "auth": self._token,
                "id": 1,
            }

            res = requests.get(self._url, data=json.dumps(data), headers=self.headers)
            group_info = res.json().get("result")
            group_info = self._parse_interfaces(group_info)

            [
                result.append(host_info)
                for host_info in group_info
                if host_info not in result
            ]

        return result

    def get_host_interfaces(self, host_name: str | list[str]) -> list[dict] | None:
        """Description
        ------
        Получение инвентаризации хостов по их именам.
        Устройство API позволяет передать массив имён хостов и получить их инвентаризацию.

        Args:
        ------
            * `host_name` (str | list[str]): имя хоста или массив с именами хостов.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        data = json.dumps(
            {
                "jsonrpc": "2.0",
                "method": "host.get",
                "params": {
                    "filter": {"host": host_name},
                    "output": ["hostid", "host", "name"],
                    "selectInterfaces": ["ip", "port", "dns"],
                },
                "auth": self._token,
                "id": 1,
            }
        )

        res = requests.get(self._url, data=data, headers=self.headers)
        info = res.json().get("result")
        info = self._parse_interfaces(info)

        return info

    def get_hosts_by_group_name(self, group_names: str | list[str]) -> list[dict]:
        """Description
        ------
        Получение хостов по имени группы.
        Не содержит данных инвентаризации и интерфейсов.

        Args:
        ------
            * `group_names` (str | list[str]): имя группы или массив имён групп.

        Returns:
        ------
            * list[dict] | None: массив данных по хостам, удовлетворающих критериям запроса.
        """

        if isinstance(group_names, str):
            group_names = [
                group_names,
            ]

        if not group_names:
            return

        result = []

        for gr_name in group_names:
            data = {
                "jsonrpc": "2.0",
                "method": "hostgroup.get",
                "params": {
                    "filter": {"name": gr_name},
                    "selectHosts": ["hostid", "host", "name", "description"],
                },
                "auth": self._token,
                "id": 1,
            }

            res = requests.get(self._url, data=json.dumps(data), headers=self.headers)

            try:
                res = res.json().get("result")[0].get("hosts")

            except Exception as err:
                logging.error(err)

            else:
                [
                    result.append(host_info)
                    for host_info in res
                    if host_info not in result
                ]

        return result

    @staticmethod
    def _parse_interfaces(data: dict | list[dict]) -> list[dict]:
        """Description
        ------
        Внутренний метод для разбора вложенного параметра интерфейсов.
        Изменяет полученные даные, раскрывая словарь "interfaces" и перенося
        данные в словарь хоста.

        Args:
        ------
            * `data` (dict | list[dict]): массив данных по хостам с ключем 'interfaces'.

        Returns:
        ------
            * list[dict]: массив данных по хостам с раскрытым интерфейсом.
        """

        if isinstance(data, dict):
            data = [data]

        for idx, host_info in enumerate(data.copy()):
            interfaces = host_info.get("interfaces")

            if interfaces:
                for key, value in interfaces[0].items():
                    data[idx][key] = value
            if data[idx].get("interfaces") or data[idx].get("interfaces") == []:
                data[idx].pop("interfaces")

        return data

    def get_graph(self, settings: dict) -> tuple[bytes, str, int]:
        """Description
        ------
        Функция получения графика по запросу к Zabbix.

        Структура возвращаемого кортежа:
            - content (bytes): График
            - url (str): Ссылка на график
            - status code (int): Код статуса запроса

        Args:
        ------
            * `settings` (dict): настройки из шаблона Zabbix

        Returns:
        ------
            * tuple[bytes, str, int]: контент по графику
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
        response = requests.get(
            url,
            params,
            cookies=self._cookies,
            verify=False,
        )

        return response.content, response.url, response.status_code

    def confirm_problem(self, settings: dict, user: User) -> int:
        """Description
        ------
        Функция, подтверждающая проблему в Zabbix.

        Args:
        ------
            * `settings` (dict): cловарь с параметрами для поиска триггера в Zabbix;
            * `user` (User): экземпляр пользователя Telegram.

        Returns:
        ------
            * status code (int): Код статуса запроса
        """

        try:
            event_id = settings["eventid"]
            data = {
                "jsonrpc": "2.0",
                "method": "event.acknowledge",
                "params": {
                    "eventids": event_id,
                    "action": 6,
                    "message": f"Problem confirm by {user.last_name} {user.first_name}",
                },
                "auth": self._token,
                "id": 1,
            }

            response = requests.post(self._url, data, headers=self.headers)
            return response.status_code

        except Exception as err:
            logging.error(err)


if __name__ == "__main__":
    pass
    # zapi = ZabbixAPI("http://130.193.42.73/zabbix/", "zabbixbot", "sexbot666")

    ### Инвентаризация по имени хоста:
    # result = zapi.get_host_interfaces(["Zabbix server", "test"])
    # zapi.output.to_console(result)
    # zapi.output.to_csv(result)

    # print()

    ### Инвентаризация по группе хоста:
    # Ищем ID группы
    # ids = zapi.get_group_id_by_group_name(["Discovered hosts", "Zabbix servers", "qq"])
    # # Выводим все хосты внутри группы
    # result = zapi.get_hosts_interfaces_by_group_id(ids)
    # zapi.output.to_console(result)
    # # zapi.output.to_csv(result)
    # zapi.output.to_excel(result)

    # print()

    ### Пачка хостов по имени группы без инвентаризации
    # result = zapi.get_hosts_by_group_name(["Discovered hosts", "Zabbix servers", "qq"])
    # zapi.output.to_console(result)
    # zapi.output.to_csv(result)
