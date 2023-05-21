#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import asyncio
import json
import io
from PIL import Image
import logging
from sys import argv
from aiogram import types
import xmltodict

from ..bot import config, bot
from ..utils.format import get_emoji, get_links, get_keyboard
from ..utils.zapi.get import get_graph
from ..utils.zapi.auth import get_cookie


logging.basicConfig(
    level=logging.INFO,
    filename="/usr/lib/zabbix/alertscripts/test.log",
    format=config.FORMAT,
)


async def test_load_to_file(argv):
    with open(
        "/usr/lib/zabbix/alertscripts/misc/test/zabbix_response.json",
        "w",
        encoding="utf-8",
    ) as fp:
        json.dump(
            {
                "send_to": argv[1],
                "subject": argv[2],
                "message": xmltodict.parse(argv[3]),
            },
            fp,
        )


async def test_send_message(args=None):
    if not args:
        with open(
            "/usr/lib/zabbix/alertscripts/misc/test/zabbix_response.json",
            "r",
            encoding="utf-8",
        ) as fp:
            data = json.load(fp)
        send_to, subject = data["send_to"], data["subject"]
        settings = data["message"]["root"]["settings"]
    else:
        try:
            send_to, subject, message = argv[1:]
            settings = message["root"]["settings"]
        except TypeError as err:
            print("Невозможно прочесть сообщение")
            return

    emoji = get_emoji(subject)
    is_graph = settings["graphs"]

    header = f"{emoji}{subject}"
    message = data["message"]["root"]["body"]["messages"]
    buttons = get_links(settings)
    tags = "#tag1 #tag2 #tag3"
    keyboard = types.InlineKeyboardMarkup(
        row_width=3,
    )

    trigger_id = settings["triggerid"]
    event_id = settings["eventid"]

    keyboard.add(
        types.InlineKeyboardButton(
            "Детали",
            url=f"{config.zabbix_api_url}tr_events.php?triggerid={trigger_id}&eventid={event_id}",
        ),
        types.InlineKeyboardButton(
            "BMC",
            url=f"{config.zabbix_api_url}tr_events.php?triggerid={trigger_id}&eventid={event_id}",
        ),
    )
    if is_graph:
        graph_img, graph_url, resp_code = get_graph(settings)
        img = Image.open(io.BytesIO(graph_img))
        img = img.resize((1000, 350))
        img.save("/usr/lib/zabbix/alertscripts/misc/test/image.png", format=img.format)

        photo = types.InputFile("/usr/lib/zabbix/alertscripts/misc/test/image.png")
        await bot.send_photo(
            send_to,
            photo,
            f"*{header}*\n\n{message}\n{buttons}\n\n{tags}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
    else:
        await bot.send_message(
            send_to,
            f"*{header}*\n\n{message}\n{buttons}\n\n{tags}",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )


if __name__ == "__main__":
    # Загрузка нового запроса от Zabbix
    # asyncio.run(test_load_to_file(argv))

    if len(argv) > 1:
        asyncio.run(test_send_message(argv))  # Запуск из Zabbix
    else:
        asyncio.run(test_send_message())  # Запуск локально
