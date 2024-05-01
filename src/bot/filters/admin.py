from aiogram.filters import BaseFilter
from aiogram.types import Message, TelegramObject, CallbackQuery
import asyncio
from src.database.controllers.ORM import ORMController


class ChatTypeFilter(BaseFilter):  # [1]
    def __init__(self, chat_type: str | list):  # [2]
        self.chat_type = chat_type

    async def __call__(self, message: Message) -> bool:  # [3]
        if isinstance(self.chat_type, str):
            return message.chat.type == self.chat_type
        else:
            return message.chat.type in self.chat_type


class ChatAdminFilter(BaseFilter):
    def __init__(self, admins_id: int):
        self.admins_id: int = admins_id

    async def __call__(self, event: TelegramObject):
        if isinstance(event, Message):
            return event.from_user.id == self.admins_id
        elif isinstance(event, CallbackQuery):
            return event.from_user.id == self.admins_id


'''
class RoleFilter(BaseFilter):
    def __init__(self, accepted_roles: list[str], db_controller: ORMController):
        self.accepted_ids: list[str] = await db_controller.role_ids(accepted_roles)
    async def __call__(self, event: TelegramObject):
        if isinstance(event, Message):
            return event.from_user.id in self.accepted_ids
'''
