from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog import StartMode
from aiogram_dialog.widgets.text import Format, Const
from aiogram_dialog.widgets.kbd import Group, Select, Button
from aiogram_dialog.widgets.input import TextInput, ManagedTextInput

from src.database.controllers.ORM import ORMController
from src.bot.utils.statesform import AdminRegistration, MainMenu
from src.bot.utils.validator import on_success, on_error

import logging

logger = logging.getLogger(__name__)
orm_controller = ORMController()


# Функции для обработки событий
async def select_role(c: CallbackQuery, widget: Select, manager: DialogManager, item_id: str):
    logger.info(f"Роль {item_id} выбрана.")
    manager.current_context().dialog_data['role_select'] = item_id
    await c.answer()


async def review_getter(dialog_manager: DialogManager, **kwargs):
    data = dialog_manager.current_context().dialog_data
    logger.debug(f"review_getter data: {data}")
    return data


async def approve_registration(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Подтверждение регистрации.")
    data = dialog_manager.current_context().dialog_data
    role = data.get("role_select")
    salary = data.get("salary_input")
    tg_id = data.get("tg_id")

    await orm_controller.update_worker_data(tg_id, role=role, salary=salary)
    await c.message.answer("✅ Заявка успешно подтверждена!")

    # Получение объекта бота через middleware_data
    bot = dialog_manager.middleware_data.get('bot')

    # Отправляем уведомление пользователю о подтверждении
    user_message = f"Ваша заявка на регистрацию была подтверждена. Ваша роль: {role}."
    if bot:
        await bot.send_message(chat_id=tg_id, text=user_message)

    # Переводим админа в главное меню
    await dialog_manager.start(MainMenu.main, mode=StartMode.RESET_STACK)

    # Завершаем диалог
    await dialog_manager.done()

# Диалог для администратора
admin_dialog = Dialog(
    Window(
        Format('У вас есть новая заявка на регистрацию от {first_name_input} {second_name_input}.\n'
               'Пожалуйста, выберите роль:'),
        Group(
            Select(
                Format("{item}"),
                id="role_select",
                items=["packer", "manager", "loader", "admin"],
                item_id_getter=lambda x: x,
                on_click=select_role,
            ),
        ),
        getter=review_getter,
        state=AdminRegistration.select_role,
    ),
    Window(
        Const("Введите зарплату:"),
        TextInput(id="salary_input", type_factory=int, on_success=on_success, on_error=on_error),
        Button(Const("✅ Подтвердить регистрацию"), id="approve_registration", on_click=approve_registration),
        getter=review_getter,
        state=AdminRegistration.enter_salary,
    ),
)
