from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from src.database.controllers.ORM import ORMController


class DatabaseMiddleware(BaseMiddleware):
    def __init__(self, controller: ORMController):
        self.controller = controller
        print("Success database middleware")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["db_controller"] = self.controller
        if isinstance(event, Message):
            data["authorized"] = await self.controller.check_worker(event.from_user.id)
        elif isinstance(event, CallbackQuery):
            data["authorized"] = await self.controller.check_worker(event.message.from_user.id)
        return await handler(event, data)
