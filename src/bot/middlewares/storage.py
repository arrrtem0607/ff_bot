from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.types import TelegramObject


class StorageMiddleware(BaseMiddleware):
    def __init__(self, storage: RedisStorage) -> None:
        self.storage: RedisStorage = storage
        print("Success message middleware")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["storage"] = self.storage
        return await handler(event, data)
