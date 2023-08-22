from aiogram import Dispatcher

from filters.admin import is_admin
from handlers import admin_handlers as a_h


def register_all_handlers(dp: Dispatcher) -> None:
    """Функция регистрации всеъ хэндлеров для бота.

    Args:
        dp (Dispatcher): Экземпляр диспетчера

    Returns:
        None
    """

    ### Инвентаризация
    # Обработка команд
    dp.register_message_handler(
        a_h.inventory_group,
        lambda ms: is_admin(ms.from_user),
        commands=["inventory_group"],
    )
    dp.register_message_handler(
        a_h.inventory_hosts,
        lambda ms: is_admin(ms.from_user),
        commands=["inventory_hosts"],
    )

    # Запрос инвентаризации через API
    dp.register_message_handler(
        a_h.get_inventory_group,
        lambda ms: is_admin(ms.from_user),
        state=a_h.AdminState.group,
    )
    dp.register_message_handler(
        a_h.get_inventory_hosts,
        lambda ms: is_admin(ms.from_user),
        state=a_h.AdminState.host_list,
    )

    # Отправка в CSV / Excel
    dp.register_callback_query_handler(
        a_h.send_inventory,
        lambda cb: cb.data.startswith("inventory_") and is_admin(cb.from_user),
    )

    dp.register_callback_query_handler(
        a_h.send_confirm_problem_to_zabbix,
        lambda cb: "confirm_problem" in cb.data and is_admin(cb.from_user),
    )
