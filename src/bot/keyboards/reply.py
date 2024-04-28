from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class ReplyKeyboards:
    def __init__(self):
        self.keyboard = ReplyKeyboardBuilder()

    def contact_kb(self) -> ReplyKeyboardMarkup:
        self.keyboard.button(text="Отправить контакт", request_contact=True)
        return self.keyboard.as_markup(resize_keyboard=True,
                                       input_field_placeholder="Жми кнопку внизу ↓")
