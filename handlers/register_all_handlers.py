from aiogram import Dispatcher

from filters.admin import is_admin
from .admin import send_actual_problems


def register_all_handlers(dp: Dispatcher) -> None:
    """Функция регистрации всеъ хэндлеров для бота.

    Args:
        dp (Dispatcher): Экземпляр диспетчера

    Returns:
        None
    """

    dp.register_message_handler(
        send_actual_problems, lambda ms: is_admin(ms.from_user), commands=["start"]
    )
