from time import time

from tabulate import tabulate
import pandas as pd
from openpyxl.worksheet.worksheet import Worksheet


class Output:
    def __init__(self) -> None:
        self.fp = "/lib/zabbix/alertscripts/misc/cache/"

    @staticmethod
    def _auto_width_column(dataframe: pd.DataFrame, worksheet: Worksheet) -> None:
        """Description
        ------
        _summary_

        _extended_summary_

        Args:
        ------
            * `dataframe` (DataFrame): _description_
            * `worksheet` (Worksheet): _description_
        """

        columns_count = len(dataframe.columns)
        rows_count = len(dataframe.values)
        headers = dataframe.columns.values

        for col_idx in range(columns_count):
            values = []

            for row_idx in range(rows_count):
                values.append(len(str(dataframe.values[row_idx][col_idx])))

            max_width = max(values)
            if max_width < len(headers[col_idx]):
                max_width = len(headers[col_idx])

            max_width += 3

            worksheet.set_column(col_idx, col_idx, max_width)

    @staticmethod
    def to_console(data: dict | list[dict]) -> None:
        """Description
        ------
        _summary_

        _extended_summary_

        Args:
        ------
            * `data` (dict | list[dict]): _description_
        """

        if isinstance(data, dict):
            data = [data]

        table = tabulate(data, "keys", "grid")
        print(table)

    def to_csv(self, data: list[dict]) -> str:
        """Description
        ------
        _summary_

        _extended_summary_

        Args:
        ------
            * `data` (list[dict]): _description_

        Returns:
        ------
            * str: _description_
        """

        if isinstance(data, dict):
            data = [data]

        fp = f"{self.fp}inventory_{time()}.csv"

        headers = max((host.keys() for host in data))

        df = pd.DataFrame(data, columns=headers)
        df.to_csv(fp, ";", header=headers, encoding="cp1251")
        # df.to_csv(fp, ";", header=headers, encoding="utf-8")

        return fp

    def to_excel(self, data: list[dict]) -> str:
        """Description
        ------
        _summary_

        _extended_summary_

        Args:
        ------
            * `data` (list[dict]): _description_

        Returns:
        ------
            * str: _description_
        """

        if isinstance(data, dict):
            data = [data]

        fp = f"{self.fp}inventory_{time()}.xlsx"
        headers = max((host.keys() for host in data))

        df = pd.DataFrame(data, columns=headers)

        with pd.ExcelWriter(fp, "xlsxwriter") as writer:
            df.to_excel(writer, "Sheet1", index=False)
            worksheet = writer.sheets["Sheet1"]
            self._auto_width_column(df, worksheet)

        return fp


def parse_interfaces(data: dict | list[dict]) -> list[dict]:
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
