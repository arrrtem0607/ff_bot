from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, User

from src.database.controllers.ORM import ORMController


class AccessMiddleware(BaseMiddleware):
    def __init__(self, allowed_roles: list):
        super().__init__()
        self.allowed_roles = allowed_roles
        self.db_controller = ORMController()

    async def __call__(
            self,
            handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
            event: Update,
            data: Dict[str, Any]
    ) -> Any:
        self.user: User = data.get('event_from_user')
        self.bot: Bot = data.get('bot')

        if User:
            user_role = await self.db_controller.get_user_role(self.user.id)
            data['role'] = user_role
            if not any(user_role in roles for roles in self.allowed_roles):
                print(self.allowed_roles)
                await self.bot.send_message(chat_id=self.user.id, text="У вас нет прав для выполнения этой команды.")
                return
        return await handler(event, data)
