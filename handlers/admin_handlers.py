import os
import re
import logging

from aiogram import types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from config import PersonalConfig, ChannelConfig
from utils.zapi.zapi import ZabbixAPI
from utils.zapi.tools import parse_interfaces
from utils.format import get_keyboard

logging.getLogger()

cfg = PersonalConfig
zapi = ZabbixAPI(cfg.zabbix_api_url, cfg.zabbix_api_login, cfg.zabbix_api_pass)


class AdminState(StatesGroup):
    group = State()
    host_list = State()

    inventory = []


# async def send_actual_problems(message: types.Message):
#     pass


async def inventory_hosts(message: types.Message):
    """
    Description
    ------
    Запрос наименования хоста у пользователя.

    Выполняется через отправку пользователю сообщения и ожидания ответа.
    Ответ будет храниться в экземпляре `AdminState` до отправки инвентаризации
    пользователю.

    Args:
    ------
        * `message` (types.Message): aiogram Message object
    """

    text = "Введите в следующем сообщении имя хоста или хостов через запятую"
    await message.answer(text)
    await AdminState.host_list.set()


async def inventory_group(message: types.Message):
    """
    Description
    ------
    Запрос наименования группы у пользователя.

    Выполняется через отправку пользователю сообщения и ожидания ответа.
    Ответ будет храниться в экземпляре `AdminState` до отправки инвентаризации
    пользователю.

    Args:
    ------
        * `message` (types.Message): aiogram Message object
    """

    text = "Введите в следующем сообщении имя группы или имена групп через запятую"
    await message.answer(text)
    await AdminState.group.set()


async def get_inventory_group(message: types.Message, state: FSMContext):
    """
    Description
    ------
    Запрос инвентаризации по имени группы или именам групп.

    Сообщение разбивается на массив имён по запятой и передаётся в `ZabbixAPI`.
    Вне зависимости от результата очищаем экземпляр `AdminState`.

    Args:
    ------
        * `message` (types.Message): aiogram Message object\n
        * `state` (FSMContext): aiogram FSMContext object

    Raises:
    ------
        * ValueError: Не удалось распознать имена групп в сообщении пользователя.
    """

    try:
        group_names = [group_name.strip() for group_name in message.text.split(",")]

        # Вариант без инвентаризации
        # data = zapi.get_hosts_by_group_name(group_names)

        # Вариант с инвентаризацией
        ids = zapi.get_group_id_by_group_name(group_names)
        data = zapi.get_hosts_interfaces_by_group_id(ids)

        if not data:
            raise ValueError(f'Wrong param "{group_names}"')

    except ValueError as err:
        logging.error(err)
        await message.answer(err)
    else:
        AdminState.inventory = data
        await ask_inventory_format(message)
    finally:
        await state.finish()


async def get_inventory_hosts(message: types.Message, state: FSMContext):
    """
    Description
    ------
    Запрос инвентаризации по имени хоста или именам хостов.

    Сообщение разбивается на массив имён по запятой и передаётся в `ZabbixAPI`.
    Вне зависимости от результата очищаем экземпляр `AdminState`.

    Args:
    ------
        * `message` (types.Message): aiogram Message object
        * `state` (FSMContext): aiogram FSMContext object

    Raises:
    ------
        * ValueError: Не удалось распознать имена хостов в сообщении пользователя.
    """

    host_list = [host.strip() for host in message.text.split(",")]

    try:
        data = zapi.get_host_interfaces(host_list)

        if not data:
            raise ValueError(f'Wrong param "{host_list}"')

    except ValueError as err:
        logging.error(err)
        await message.answer(err)

    else:
        data = parse_interfaces(data)
        AdminState.inventory = data
        await ask_inventory_format(message)
    finally:
        await state.finish()


async def ask_inventory_format(message: types.Message):
    """
    Description
    ------
    Вывод меню с запросом варианта выгрузки файла с инвентаризацией по узлу или
    группе.

    Args:
    ------
        * `message` (types.Message): aiogram Message object
    """

    kb = types.InlineKeyboardMarkup().add(
        types.InlineKeyboardButton("CSV", callback_data="inventory_csv"),
        types.InlineKeyboardButton("Excel", callback_data="inventory_excel"),
    )
    await message.answer("Выберите формат данных:", reply_markup=kb)


async def send_inventory(callback: types.CallbackQuery):
    """
    Description
    ------
    Отправка файла с данными инвентаризации узла или группы.
    Автоматически подстраивается под выбор пользователя.

    Args:
    ------
        * `callback` (types.CallbackQuery): aiogram CallbackQuery object
    """
    data = AdminState.inventory

    if callback.data == "inventory_csv":
        fp = zapi.output.to_csv(data)
        file = types.InputFile(fp)
    else:
        fp = zapi.output.to_excel(data)
        file = types.InputFile(fp)

    await callback.message.answer_document(file)
    await callback.bot.answer_callback_query(callback.id)

    if os.path.exists(fp):
        os.remove(fp)


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
        await callback_query.bot.edit_message_reply_markup(
            callback_query.message.chat.id,
            callback_query.message.message_id,
            callback_query.inline_message_id,
            get_keyboard(settings, cfg, True),
        )
