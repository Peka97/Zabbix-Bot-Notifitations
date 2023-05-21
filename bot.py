#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import logging
import re

from aiogram import Bot, Dispatcher, executor, types

from config import *
from handlers.register_all_handlers import register_all_handlers
from utils.zapi.update_acknowledge import confirm_problem
from utils.format import get_keyboard


config = BaseConfig()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    # filename="/usr/lib/zabbix/alertscripts/log.log",
    format=config.FORMAT,
)

# Initialize bot and dispatcher
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)


@dp.callback_query_handler(lambda c: "confirm_problem" in c.data)
async def send_confirm_problem_to_zabbix(callback_query: types.CallbackQuery):
    user = callback_query.from_user
    message = callback_query.message.caption
    settings = {
        "itemid": re.findall(r"#item_\d+", message)[0].split("_")[1],
        "eventid": re.findall(r"#event_\d+", message)[0].split("_")[1],
        "triggerid": re.findall(r"#trigger_\d+", message)[0].split("_")[1],
        "period": re.findall(r"#period_\d+", message)[0].split("_")[1],
        "keyboard": "True",
    }
    confirm_problem(settings, user)

    await bot.edit_message_reply_markup(
        callback_query.message.chat.id,
        callback_query.message.message_id,
        callback_query.inline_message_id,
        get_keyboard(settings, config, True),
    )


if __name__ == "__main__":
    register_all_handlers(dp)
    executor.start_polling(dp, skip_updates=True)
