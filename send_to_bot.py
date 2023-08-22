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
from utils.zapi.zapi import ZabbixAPI


# Устанавливаем необходимую конфигурацию
config = PersonalConfig

# Логирование
logging.basicConfig(
    level=logging.INFO,
    filename="/usr/lib/zabbix/alertscripts/logs/send_to_bot.log",
    format=config.FORMAT,
)

# Создаем экземпляр бота
bot = Bot(token=config.API_TOKEN)
zapi = ZabbixAPI(config.zabbix_api_url, config.zabbix_api_login, config.zabbix_api_pass)


async def send_message(*args: list) -> None:
    """Функция, принимающая на вход список данных, содержащих следующую
    информацию:
        script_name - имя вызванного скрипта (не будет использован).
        send_to - ID на который нужно отправить сообщение в Telegram
        subject - описание проблемы
        message - xml объект с дополнительной информацией по проблеме Zabbix

    Args:
        argv (list): коллекция данных
    """

    # Пробуем сериализовать полученные данные
    try:
        send_to, subject, message = args[1:]
        message = xmltodict.parse(message)
        settings = message["root"]["settings"]
        text = message["root"]["body"]["messages"]
        is_graph = True if settings.get("graphs") == "True" else False

    except ValueError:
        logging.error(f"Нет аргументов для отправки", exc_info=True)
        session = await bot.get_session()

        if session:
            await session.close()
        return
    except (KeyError, ExpatError):
        logging.error(f"Некорректные настройки шаблона", exc_info=True)
        for admin in config.ADMINS:
            await bot.send_message(admin, f"Ошибка шаблона")

        session = await bot.get_session()

        if session:
            await session.close()
        return

    # Выбор канала супергруппы, если необходима
    # thread_id = send_to if send_to in config.THREAD_IDS.values() else None

    # Формируем сообщение для отправки
    emoji_1, emoji_2 = get_emoji(subject, settings)
    header = f"{emoji_1}{subject}"
    crit_idx = text.index("Критичность:") + len("Критичность:")
    text = f"{text[:crit_idx]} {emoji_2} {text[crit_idx:]}"

    # Формируем тэги
    item_id = settings["itemid"]
    event_id = settings["eventid"]
    trigger_id = settings["triggerid"]
    period = settings["graphperiod"] if settings.get("graphperiod") else config.period
    tags = (
        f"#item\_{item_id} #event\_{event_id} #trigger\_{trigger_id} #period\_{period}"
    )

    # Отправка сообщения с графиком
    if is_graph:
        # Пробуем отправить сообщение
        try:
            # Скачиваем график по ссылке
            graph_img, resp, _ = zapi.get_graph(settings)
            img = Image.open(io.BytesIO(graph_img))

            # Объявляем путь для графика
            img_name = f"{settings['host']}_{settings['triggerid']}_graph.png"
            img_path = f"/usr/lib/zabbix/alertscripts/misc/cache/{img_name}"

            # Проверяем разрешение графика
            if img.size < (config.graph_width, config.graph_height):
                raise ValueError

            # Изменяем размеры графика под стандарты Telegram и сохраняем
            img = img.resize((1000, 350))
            img.save(img_path, format=img.format)

            # Загружаем график объектом, который распознает Telegram
            photo = types.InputFile(img_path)

        # Отлавливаем ошибки
        except Exception as err:
            logging.error(f"Ошибка отправки графика:\n {err}", exc_info=True)

            img_err_path = "/usr/lib/zabbix/alertscripts/misc/img/graph_not_found.png"
            photo = types.InputFile(img_err_path)

        # Вне зависимости от результата удаляем файл из папки кэша
        else:
            if os.path.exists(img_path):
                os.remove(img_path)
        finally:
            await bot.send_photo(
                send_to,
                photo,
                f"*{header}*\n\n{text}\n\n{tags}",
                parse_mode="Markdown",
                reply_markup=get_keyboard(settings, config),
            )

    # Отправка сообщения без графика
    else:
        try:
            await bot.send_message(
                send_to,
                f"*{header}*\n\n{text}\n\n{tags}",
                parse_mode="Markdown",
                reply_markup=get_keyboard(settings, config),
            )

        # Отлавливаем ошибки
        except Exception as err:
            logging.error(f"Ошибка отправки сообщения:\n {err}", exc_info=True)

    # Закрываем сессию бота
    session = await bot.get_session()
    if session:
        await session.close()


if __name__ == "__main__":
    asyncio.run(send_message(*argv))
