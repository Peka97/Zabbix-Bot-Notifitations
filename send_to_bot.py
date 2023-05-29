#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import os
import asyncio
import io
from PIL import Image
import logging
from sys import argv
import xmltodict
from xml.parsers.expat import ExpatError
from aiogram import types, Bot

from config import *
from utils.format import get_emoji, get_keyboard
from utils.zapi.get import get_graph

config = PersonalConfig

# Configure logging
logging.basicConfig(
    level=logging.ERROR,
    filename="/usr/lib/zabbix/alertscripts/log.log",
    format=config.FORMAT,
)

bot = Bot(token=config.API_TOKEN)


async def send_message(argv: list) -> None:
    try:
        send_to, subject, message = argv[1:]
        message = xmltodict.parse(message)
        settings = message["root"]["settings"]
        text = message["root"]["body"]["messages"]
        is_graph = True if settings.get("graphs") == "True" else False

    except ValueError:
        logging.error(f"Нет аргументов для отправки. Subject: {subject}", exc_info=True)
        await bot.session.close()
        return
    except KeyError:
        logging.error(f"Некорректные настройки. Subject: {subject}", exc_info=True)
        await bot.session.close()
        return
    except ExpatError:
        logging.error(f"Некорректное сообщение. Subject: {subject}", exc_info=True)
        for admin in config.ADMINS:
            await bot.send_message(admin, f"Ошибка шаблона\nSubject: {subject}")
        await bot.session.close()
        return

    # thread_id = send_to if send_to in config.THREAD_IDS.values() else None

    emoji_1, emoji_2 = get_emoji(subject, settings)
    header = f"{emoji_1}{subject}"
    crit_idx = text.index("Критичность:") + len("Критичность:")
    text = f"{text[:crit_idx]} {emoji_2} {text[crit_idx:]}"

    item_id = settings["itemid"]
    event_id = settings["eventid"]
    trigger_id = settings["triggerid"]
    period = settings["graphperiod"] if settings.get("graphperiod") else config.period
    tags = (
        f"#item\_{item_id} #event\_{event_id} #trigger\_{trigger_id} #period\_{period}"
    )

    if is_graph:
        try:
            graph_img, _, _ = get_graph(settings, config)
            img = Image.open(io.BytesIO(graph_img))
            img = img.resize((1000, 350))
            img_name = f"{settings['host']}_{settings['triggerid']}_graph.png"
            img_path = f"/usr/lib/zabbix/alertscripts/misc/cache/{img_name}"
            img.save(img_path, format=img.format)

            photo = types.InputFile(img_path)
            await bot.send_photo(
                send_to,
                photo,
                f"*{header}*\n\n{text}\n\n{tags}",
                parse_mode="Markdown",
                reply_markup=get_keyboard(settings, config),
            )
        finally:
            os.remove(img_path)
    else:
        await bot.send_message(
            send_to,
            f"*{header}*\n\n{text}\n\n{tags}",
            parse_mode="Markdown",
            reply_markup=get_keyboard(settings, config),
        )
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(send_message(argv))
