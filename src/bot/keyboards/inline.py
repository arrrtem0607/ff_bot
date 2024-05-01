from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from src.bot.utils.callbackfabric import *


class InlineKeyboards:
    def __init__(self):
        self.keyboard = InlineKeyboardBuilder()

    def menu(self, role):
        if role == 'admin':
            self.keyboard.button(text='Статистика по работникам', callback_data='status')
            self.keyboard.button(text='Добавить новый товар', callback_data='add')
            self.keyboard.button(text='Изменить текущий товар', callback_data='change_sku')
            self.keyboard.button(text="Изменить информацию о сотрудниках", callback_data='change_worker')
        elif role == 'packer':
            self.keyboard.button(text='Начать упаковку', callback_data='start_packing')
        elif role == 'loader':
            self.keyboard.button(text='Начать упаковку', callback_data='start_packing')
            self.keyboard.button(text='Уйти на погрузку', callback_data='start_loading')
        return self.keyboard.adjust(3).as_markup()

    def admin_choice(self, tg_id: int,
                     username: str,
                     phone: str,
                     name: str) -> InlineKeyboardMarkup:
        accept_data = AcceptChoice(accept=True, tg_id=tg_id, username=username, phone=phone, name=name)
        reject_data = AcceptChoice(accept=False, tg_id=tg_id, username=username, phone=phone, name=name)
        self.keyboard.button(text="Одобрить ✅", callback_data=accept_data)
        self.keyboard.button(text="Отклонить ❌", callback_data=reject_data)
        self.keyboard.adjust(2)
        return self.keyboard.as_markup()

    def end_packing(self):
        self.keyboard.button(text='Закончить упаковку', callback_data='end_packing')
        self.keyboard.adjust(1)
        return self.keyboard.as_markup()

    async def build_goods_keyboard(self, goods):
        for good in goods:
            self.keyboard.button(text=f"{good.sku}",
                                 callback_data=f"choose_{good.sku}")
        self.keyboard.adjust(3)
        return self.keyboard.as_markup()

    async def choose_sku_field(self):
        self.keyboard.button(text='Название',
                             callback_data='name')
        self.keyboard.button(text='Техническое задание',
                             callback_data='technical_task')
        self.keyboard.button(text='Ссылка на видео',
                             callback_data='video_url')
        return self.keyboard.adjust(3).as_markup()

    async def choose_worker_field(self):
        self.keyboard.button(text='Никнейм',
                             callback_data='username')
        self.keyboard.button(text='Имя',
                             callback_data='name')
        self.keyboard.button(text='Должность',
                             callback_data='role')
        self.keyboard.button(text='Зарплата',
                             callback_data='salary')
        return self.keyboard.adjust(3).as_markup()

    async def build_workers_keyboard(self, workers):
        for worker in workers:
            self.keyboard.button(text=f"{worker.name}",
                                 callback_data=f"choose_{worker.name}")
        self.keyboard.adjust(3)
        return self.keyboard.as_markup()

    def choose_role(self):
        self.keyboard.button(text='Администратор', callback_data='admin')
        self.keyboard.button(text='Упаковщик', callback_data='packer')
        self.keyboard.button(text='Грузчик', callback_data='loader')
        self.keyboard.button(text='Менеджер', callback_data='manager')
        return self.keyboard.adjust(3).as_markup()

    # def start_loading(self):

    def end_loading(self):
        self.keyboard.button(text='Закончить погрузку/разгрузку',
                             callback_data='end_loading')
