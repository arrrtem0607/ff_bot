from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, StartMode, Window
from aiogram_dialog.widgets.text import Const, Format, Multi
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button

import logging
from functools import partial
from datetime import datetime

from src.bot.utils.statesform import Registration
from src.bot.utils.validator import (
    validate_name,
    validate_bank_name,
    validate_payment_details,
    validate_phone_number,
    validate_date,
    on_success,
    on_error
)
from src.database.controllers.ORM import ORMController

logger = logging.getLogger(__name__)
orm_controller = ORMController()


async def get_values(dialog_manager: DialogManager, keys: list, **kwargs):
    context_data = dialog_manager.current_context().dialog_data
    data = {key: context_data.get(key, None) for key in keys}

    # Логирование данных для отладки
    logger.debug(f"get_values data: {data}, context: {context_data}")

    return data


async def confirm_data(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    logger.info("Подтверждение данных.")
    data = dialog_manager.current_context().dialog_data

    # Преобразуем дату рождения в объект datetime
    birth_date_str = data.get("birth_date_input")
    birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d")

    worker_data = {
        "first_name": data.get("first_name_input"),
        "second_name": data.get("second_name_input"),
        "phone_number": data.get("number_input"),
        "payment_details": data.get("payment_details_input"),
        "bank_name": data.get("bank_name_input"),
        "date_of_birth": birth_date.strftime("%Y-%m-%d"),
        "role": "pending",
        "tg_id": c.from_user.id,
        "status": "pending"
    }
    await orm_controller.create_worker(worker_data)
    await dialog_manager.start(
        Registration.awaiting_approval, mode=StartMode.RESET_STACK
    )


registration_dialog = Dialog(
    Window(
        Multi(
            Const('👋 Привет!\n'),
            Const('Добро пожаловать на наш фулфилмент! '
                  'Для начала работы нам нужно немного информации.\n'),
            Const('Давайте познакомимся! Пожалуйста, введите ваше имя:'),
            sep='\n'
        ),
        TextInput(
            id='first_name_input',
            type_factory=validate_name,
            on_success=on_success,
            on_error=on_error
        ),
        state=Registration.get_first_name,
    ),
    Window(
        Multi(
            Format('Приятно познакомиться, {first_name_input}! 😊'),
            Const('Теперь введите вашу фамилию:'),
            sep='\n'
        ),
        TextInput(
            id='second_name_input',
            type_factory=validate_name,
            on_success=on_success,
            on_error=on_error
        ),
        Back(id="back_to_first_name", text=Const("Назад")),
        getter=partial(get_values, keys=["first_name_input"]),
        state=Registration.get_second_name,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 🎂'),
            Const('Введите вашу дату рождения (ДД.ММ.ГГГГ):'),
            sep='\n'
        ),
        TextInput(
            id='birth_date_input',
            type_factory=validate_date,
            on_success=on_success,
            on_error=on_error
        ),
        Back(id="back_to_second_name", text=Const("Назад")),
        getter=partial(get_values, keys=["first_name_input", "second_name_input"]),
        state=Registration.get_birth_date,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 📞'),
            Const('Теперь, пожалуйста, введите ваш номер телефона для связи:'),
            sep='\n'
        ),
        TextInput(
            id='number_input',
            type_factory=validate_phone_number,
            on_success=on_success,
            on_error=on_error
        ),
        Back(id="back_to_birth_date", text=Const("Назад")),
        getter=partial(get_values, keys=["first_name_input", "second_name_input"]),
        state=Registration.get_number,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 💳'),
            Const('Введите реквизиты для выплаты заработной платы '
                  '(номер банковской карты или номер телефона):'),
            sep='\n'
        ),
        TextInput(
            id='payment_details_input',
            type_factory=validate_payment_details,
            on_success=on_success,
            on_error=on_error
        ),
        Back(id="back_to_number", text=Const("Назад")),
        getter=partial(get_values, keys=["first_name_input", "second_name_input"]),
        state=Registration.get_payment_details,
    ),
    Window(
        Multi(
            Format('Отлично, {first_name_input} {second_name_input}! 🏦'),
            Const('Введите название вашего банка:'),
            sep='\n'
        ),
        TextInput(
            id='bank_name_input',
            type_factory=validate_bank_name,
            on_success=on_success,
            on_error=on_error
        ),
        Back(id="back_to_payment_details", text=Const("Назад")),
        getter=partial(get_values, keys=["first_name_input", "second_name_input", "payment_details_input"]),
        state=Registration.get_bank_name,
    ),
    Window(
        Multi(
            Format('Пожалуйста, проверьте введенные данные:\n'
                   'Имя: {first_name_input}\n'
                   'Фамилия: {second_name_input}\n'
                   'Дата рождения: {birth_date_input}\n'
                   'Телефон: {number_input}\n'
                   'Реквизиты: {payment_details_input}\n'
                   'Банк: {bank_name_input}'),
            Const('\nЕсли все верно, подтвердите данные. '
                  'После регистрации их можно будет изменить через главное меню.'),
            sep='\n'
        ),
        Back(id="back_to_bank_name", text=Const("Назад")),
        Button(id="final_confirm", text=Const("Подтвердить"), on_click=confirm_data),
        getter=partial(get_values, keys=[
            "first_name_input", "second_name_input",
            "birth_date_input", "number_input",
            "payment_details_input", "bank_name_input"
        ]),
        state=Registration.review_data,
    ),
    Window(
        Const("✅Ваша заявка на регистрацию принята. Пожалуйста, дождитесь подтверждения от администратора."),
        state=Registration.awaiting_approval
    ),
)
