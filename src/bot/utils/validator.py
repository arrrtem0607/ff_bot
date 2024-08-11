import re
import logging
from datetime import datetime

from aiogram.types import Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.input import ManagedTextInput


logger = logging.getLogger(__name__)


async def on_success(event, widget, dialog_manager: DialogManager, data):
    # Сохраняем значение в dialog_data явно
    key = widget.widget_id
    dialog_manager.current_context().dialog_data[key] = data
    await dialog_manager.next()


async def on_error(message: Message, widget: ManagedTextInput, dialog_manager: DialogManager, error: Exception):
    logger.error(f"Ошибка валидации для {widget.widget_id}: {error}")
    await message.answer(text=f"⚠️ Ошибка: {str(error)}")


def validate_name(name: str) -> str:
    if not re.match(r'^[а-яА-ЯёЁ]+$', name):
        raise ValueError("Имя должно содержать только буквы кириллицы")
    return name.capitalize()


def validate_phone_number(phone: str) -> str:
    patterns = [
        r'^\+7\d{10}$',
        r'^7\d{10}$',
        r'^8\d{10}$',
        r'^\d{10}$'
    ]
    if not any(re.match(pattern, phone) for pattern in patterns):
        raise ValueError("Номер телефона должен соответствовать одному из шаблонов\n"
                         "+7...(10 цифр)\n"
                         "7...(10 цифр)\n"
                         "8...(10 цифр)\n"
                         "10 цифр\n")

    phone = re.sub(r'^[78]', '+7', phone) if phone.startswith(('7', '8')) else f'+7{phone}'
    return phone


def validate_payment_details(details: str) -> str:
    return validate_phone_number(details)  # Используем ту же валидацию, что и для номера телефона


def validate_bank_name(bank: str) -> str:
    if not re.match(r'^[а-яА-ЯёЁ\s]+$', bank):
        raise ValueError("Название банка должно содержать только буквы кириллицы и пробелы")
    return bank.capitalize()


def validate_date(value: str) -> datetime.date:
    formats = ["%d %m %Y", "%d.%m.%y", "%d %m %y", "%d.%m.%Y"]
    for fmt in formats:
        try:
            date = datetime.strptime(value, fmt)
            if date.year < 100:
                date = date.replace(year=date.year + 2000)
            return date.date().isoformat()
        except ValueError:
            continue
    raise ValueError("Некорректный формат даты. Пожалуйста, "
                     "введите дату в одном из следующих форматов: ДД.ММ.ГГГГ, ДД.ММ.ГГ или ДД ММ ГГГГ.")
