from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.configurations import MainConfig


class ConfigMiddleware(BaseMiddleware):
    def __init__(self, config: MainConfig):
        self.config: MainConfig = config
        print("Success config middleware")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["config"] = self.config
        return await handler(event, data)
