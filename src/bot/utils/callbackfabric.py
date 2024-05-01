import datetime

from aiogram.filters.callback_data import CallbackData


class Gender(CallbackData, prefix='Gender'):
    gender: str


class AcceptChoice(CallbackData, prefix='AcceptChoice'):
    accept: bool
    tg_id: int
    username: str
    phone: str
    name: str


class UserAnswer(CallbackData, prefix='UserAnswer'):
    yes: bool = False
    no: bool = False


class Admin(CallbackData, prefix='Admin'):
    show_token: bool = False
    check_donate: bool = False
    frequency: bool = False
    time_last: bool = False
    api: bool = False
