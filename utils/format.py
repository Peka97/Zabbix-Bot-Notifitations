from aiogram import types


def get_emoji(subj: str, settings) -> str | None:
    emojies = {
        "Problem": "🚨",
        "Resolved": "✅",
        "Update": "🚧",
        "Not classified": "⁉️",
        "Information": "💙",
        "Warning": "💛",
        "Average": "🧡",
        "High": "❤️",
        "Disaster": "💔",
        "Test": "🚽💩",
    }

    emoji_1 = emojies.get(subj.split()[0].rstrip(":"))
    emoji_2 = emojies.get(settings.get("criticality"))

    return emoji_1, emoji_2


def get_keyboard(
    settings: dict, config, edit=False
) -> types.InlineKeyboardMarkup | None:
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
        if edit:
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
                types.InlineKeyboardButton("Проблема ✅", callback_data="empty"),
            )
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
