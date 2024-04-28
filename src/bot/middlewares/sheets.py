from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from src.google_sheets.controllers.google import SheetsController


class SheetsMiddleware(BaseMiddleware):
    def __init__(self, controller: SheetsController):
        self.controller = controller
        print("Success Google Sheets middleware")

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        data["sheets_controller"] = self.controller
        return await handler(event, data)
