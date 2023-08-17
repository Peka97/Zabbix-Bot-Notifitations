#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import logging
import re

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import *
from handlers.register_all_handlers import register_all_handlers
from utils.format import get_keyboard
from utils.zapi.zapi import ZabbixAPI


# Определение конфигурации
config = BaseConfig()

# Логирование
logging.basicConfig(
    level=logging.INFO,
    # filename="/usr/lib/zabbix/alertscripts/logs/bot.log",
    format=config.FORMAT,
)

# Объявление экземпляров бота, диспетчера и ZappixAPI
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())
zapi = ZabbixAPI(config.zabbix_api_url, config.zabbix_api_login, config.zabbix_api_pass)


@dp.callback_query_handler(lambda c: "confirm_problem" in c.data)
async def send_confirm_problem_to_zabbix(callback_query: types.CallbackQuery) -> None:
    """Функция, отправляющая запрос подтверждения триггера в Zabbix.

    Args:
        callback_query (types.CallbackQuery): Экземпляр callback Telegram

    Returns:
        None
    """

    # Определяем от кого отправлен callback
    user = callback_query.from_user

    # Читаем параметры из тегов сообщения, под которым была нажата
    # inline-кнопка, для определения триггера
    message = callback_query.message.caption
    settings = {
        "itemid": re.findall(r"#item_\d+", message)[0].split("_")[1],
        "eventid": re.findall(r"#event_\d+", message)[0].split("_")[1],
        "triggerid": re.findall(r"#trigger_\d+", message)[0].split("_")[1],
        "period": re.findall(r"#period_\d+", message)[0].split("_")[1],
        "keyboard": "True",
    }

    # Подверждаем проблему
    status_code = zapi.confirm_problem(settings, user)

    # При статусе 200 редактируем клавиатуру
    if status_code == 200:
        await bot.edit_message_reply_markup(
            callback_query.message.chat.id,
            callback_query.message.message_id,
            callback_query.inline_message_id,
            get_keyboard(settings, config, True),
        )


async def start_up(dp: Dispatcher):
    """Description
    ------
    _summary_

    _extended_summary_

    Args:
    ------
        * `dp` (Dispatcher): _description_
    """

    for user_id in config.ADMINS:
        commands = [
            types.BotCommand("inventory_hosts", "Инвентаризация хостов"),
            types.BotCommand("inventory_group", "Инвентаризация группы"),
        ]
        scope = types.BotCommandScopeChat(user_id)
        await bot.set_my_commands(commands, scope)


if __name__ == "__main__":
    # Регистрируем все хэндлеры для бота
    register_all_handlers(dp)
    # Запускаем бота
    executor.start_polling(dp, skip_updates=True, on_startup=start_up)
