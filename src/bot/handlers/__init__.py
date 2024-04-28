from aiogram import Router
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.bot.middlewares.sheets import SheetsMiddleware
from src.configurations import MainConfig
from src.bot.handlers.admin import router as admin_router
from src.bot.handlers.user import router as user_router
from src.bot.middlewares.config import ConfigMiddleware
from src.bot.middlewares.storage import StorageMiddleware
from src.bot.middlewares.scheduler import ApschedulerMiddleware
from src.bot.middlewares.database import DatabaseMiddleware
from src.bot.filters.admin import ChatAdminFilter, ChatTypeFilter
from src.bot.handlers.start_end import router as start_end_router
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController


async def get_all_routers(storage: RedisStorage, admins_id: int, scheduler: AsyncIOScheduler,
                          orm_controller: ORMController,
                          config: MainConfig,
                          sheets_controller: SheetsController) -> Router:
    start_end_router.message.middleware(ConfigMiddleware(config))

    user_router.message.middleware(StorageMiddleware(storage))
    user_router.callback_query.middleware(StorageMiddleware(storage))
    user_router.message.middleware(ConfigMiddleware(config))
    user_router.callback_query.middleware(ConfigMiddleware(config))
    user.router.message.middleware(DatabaseMiddleware(orm_controller))
    user.router.callback_query.middleware(DatabaseMiddleware(orm_controller))
    user.router.message.middleware(SheetsMiddleware(sheets_controller))
    user.router.callback_query.middleware(SheetsMiddleware(sheets_controller))

    admin.router.message.middleware(DatabaseMiddleware(orm_controller))
    admin_router.callback_query.middleware(DatabaseMiddleware(orm_controller))
    admin_router.message.middleware(StorageMiddleware(storage))
    admin_router.callback_query.middleware(StorageMiddleware(storage))
    admin_router.callback_query.middleware(ApschedulerMiddleware(scheduler))
    admin_router.message.filter(ChatAdminFilter(admins_id))
    admin_router.callback_query.filter(ChatAdminFilter(admins_id))
    admin.router.message.middleware(SheetsMiddleware(sheets_controller))
    admin.router.callback_query.middleware(SheetsMiddleware(sheets_controller))

    router: Router = Router()
    router.message.filter(ChatTypeFilter("private"))

    router.include_routers(
        start_end_router, user_router, admin_router
    )
    return router
