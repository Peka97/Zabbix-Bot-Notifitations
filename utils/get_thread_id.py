#!/usr/lib/zabbix/alertscripts/.venv/bin/python3

################################################################################
#                                                                              #
#      Данный скрипт служит помощником для определения Chat ID и Thread ID     #
#                       в чате\супергруппе Telegram                            #
#                                                                              #
################################################################################

from aiogram import Dispatcher, Bot, types, executor

from config import PersonalConfig

config = PersonalConfig

bot = Bot(config.API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def send_chat_info(message: types.Message):
    text = f"Chat ID: {message.chat.id}\nThread ID: {message.message_thread_id}"
    await message.answer(text)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
