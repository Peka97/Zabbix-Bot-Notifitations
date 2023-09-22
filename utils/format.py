from aiogram import types


def get_emoji(subj: str, settings: dict) -> str | None:
    """Функция, подбирающая необходимый эмоджи под сообщение.

    Args:
        subj (str): Проблема из параметров Zabbix
        settings (dict): Настройки из шаблона Zabbix

    Returns:
        str | None: Эмоджи
    """

    emojies = {
        "Problem": "🚨",
        "Resolved": "✅",
        "Update": "🚧",
        "Not classified": "⁉️",
        "Information": "🔵",
        "Warning": "🟡",
        "Average": "🟠",
        "High": "🔴",
        "Disaster": "⛔️",
        "Test": "🛠",
    }

    emoji_1 = emojies.get(subj.split()[0].rstrip(":"))
    emoji_2 = emojies.get(settings.get("criticality"))

    return emoji_1, emoji_2


def get_keyboard(
    settings: dict, config: object, edit=False
) -> types.InlineKeyboardMarkup | None:
    """Функция генерации Inline-клавиатуры для сообщений на основе переданных
    из Zabbix настроек и выбранной конфигурации.

     - если клавитура формируется впервые, то флаг edit оставляем по умолчанию
       False.
     - если нужно обновить клавиатуру (подтвердить проблему в Zabbix), то
       в edit передаём True.

    Args:
        settings (dict): Настройки из шаблона Zabbix
        config (object): Конфигурация скрипта
        edit (bool, optional): Отредактировать клавиатуру под существующим
        сообщением. По умолчанию False.

    Returns:
        types.InlineKeyboardMarkup | None: Экземпляр Inline-клавиатуры.
    """

    # Проверяем флаг "keyboard" чтобы понять нужна ли нам клавиатура в сообщении
    if settings.get("keyboard") and settings["keyboard"] == "True":
        item_id = settings["itemid"]
        event_id = settings["eventid"]
        trigger_id = settings["triggerid"]
        period = (
            settings["graphperiod"] if settings.get("graphperiod") else config.period
        )
        keyboard = types.InlineKeyboardMarkup(
            row_width=2,
        )

        # Проверка флага на исправление существующей клавиатуры
        if edit:
            # Формируем клавиатуру с подтверждённой проблемой
            keyboard.add(
                types.InlineKeyboardButton(
                    "График 📈",
                    url=f"{config.zabbix_api_url}history.php?action=showgraph&itemids[]={item_id}&from=now-{period}",
                ),
                types.InlineKeyboardButton(
                    "Детали 📋",
                    url=f"{config.zabbix_api_url}tr_events.php?triggerid={trigger_id}&eventid={event_id}",
                ),
                types.InlineKeyboardButton(
                    "BMC 🗳",
                    url=f"{config.zabbix_api_url}",
                ),
                types.InlineKeyboardButton("Подтверждено ✅", callback_data="empty"),
            )

        # Формируем новую клавиатуру
        else:
            keyboard.add(
                types.InlineKeyboardButton(
                    "График 📈",
                    url=f"{config.zabbix_api_url}history.php?action=showgraph&itemids[]={item_id}&from=now-{period}",
                ),
                types.InlineKeyboardButton(
                    "Детали 📋",
                    url=f"{config.zabbix_api_url}tr_events.php?triggerid={trigger_id}&eventid={event_id}",
                ),
                types.InlineKeyboardButton("BMC 🗳", url=f"{config.zabbix_api_url}"),
                types.InlineKeyboardButton(
                    "Подтвердить 📌", callback_data="confirm_problem"
                ),
            )
        return keyboard

    return None
