import logging
from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware, Bot
from aiogram.types import Update, User

from src.database.controllers.ORM import ORMController

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Добавляем обработчик для записи логов в файл
file_handler = logging.FileHandler('/Users/DlyaNas/Desktop/Работы/MPWAVE/Автоматизация/ff_bot/application.log')
file_handler.setLevel(logging.INFO)

# Настраиваем формат логов
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(file_handler)


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
        user: User = data.get('event_from_user')
        bot: Bot = data.get('bot')

        if user:
            logger.info(f"Проверка роли для пользователя с ID: {user.id}")
            user_role = await self.db_controller.get_user_role(user.id)
            data['role'] = user_role

            # Логирование роли пользователя
            logger.info(f"Роль пользователя: {user_role}")

            # Проверка, если пользователь имеет разрешенную роль
            if not any(user_role in roles for roles in self.allowed_roles):
                logger.warning(
                    f"Пользователь с ID: {user.id} не имеет прав для выполнения команды. "
                    f"Требуемые роли: {self.allowed_roles}")
                await bot.send_message(chat_id=user.id, text="У вас нет прав для выполнения этой команды.")
                return

            # Логирование успешного доступа
            logger.info(f"Пользователь с ID: {user.id} имеет доступ для выполнения команды.")
        else:
            logger.error("Пользователь не найден в данных события")

        return await handler(event, data)
