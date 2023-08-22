#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import PersonalConfig, ChannelConfig
from handlers.register_all_handlers import register_all_handlers


# Определение конфигурации
config = PersonalConfig()

# Логирование
logging.basicConfig(
    level=logging.ERROR,
    filename="/usr/lib/zabbix/alertscripts/logs/bot.log",
    format=config.FORMAT,
)

# Объявление экземпляров бота, диспетчера и ZappixAPI
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


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
