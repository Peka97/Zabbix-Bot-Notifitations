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
