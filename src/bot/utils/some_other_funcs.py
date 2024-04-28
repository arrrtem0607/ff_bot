from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import Message
from aiogram import Bot
from src.keyboards.inline import InlineKeyboards


async def return_to_menu(message: Message, storage: RedisStorage, callback: bool = False):
    show_mode: bytes = await storage.redis.get("show_token")
    mode: bytes = await storage.redis.get("check_donate")
    frequency: str = (await storage.redis.get("frequency")).decode()
    last_donate: str = (await storage.redis.get("time_last")).decode()
    if callback:
        await message.edit_text("<b>Добро пожаловать в меню. 👨‍💻</b>\n"
                                "_____________\n"
                                f"Показывать обновления токена:"
                                f" {'включён' if int(show_mode) else 'выключен'}\n"
                                f"Текущий режим опроса: {'включён' if int(mode) else 'выключен'}\n"
                                f"Частота проверки донатов: 1 запрос / {frequency} мин.\n"
                                f"Количество минут с последнего доната: {last_donate} мин.",
                                reply_markup=await InlineKeyboards().admin(storage))
    else:
        await message.answer("<b>Добро пожаловать в меню. 👨‍💻</b>\n"
                             "_____________\n"
                             f"Текущий режим показа обновления токена: {'включён' if int(show_mode) else 'выключен'}\n"
                             f"Текущий режим опроса: {'включён' if int(mode) else 'выключен'}\n"
                             f"Частота проверки донатов: 1 запрос / {frequency} мин.\n"
                             f"Количество минут с последнего доната: {last_donate} мин.",
                             reply_markup=await InlineKeyboards().admin(storage))
