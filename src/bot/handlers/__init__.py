from aiogram import Router
from aiogram.fsm.storage.redis import RedisStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src.bot.middlewares.sheets import SheetsMiddleware
from src.configurations import MainConfig
from src.bot.handlers.admin import router as admin_router
from src.bot.handlers.packer import router as packer_router
from src.bot.handlers.loader import router as loader_router
from src.bot.middlewares.config import ConfigMiddleware
from src.bot.middlewares.storage import StorageMiddleware
from src.bot.middlewares.scheduler import ApschedulerMiddleware
from src.bot.middlewares.database import DatabaseMiddleware
from src.bot.middlewares.role import AccessMiddleware
from src.bot.filters.admin import ChatTypeFilter
from src.bot.handlers.start_end import router as start_end_router
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController


async def get_all_routers(storage: RedisStorage,
                          admins_id: int,
                          admins_rights: list,
                          packers_rights: list,
                          managers_rights: list,
                          loaders_rights: list,
                          scheduler: AsyncIOScheduler,
                          orm_controller: ORMController,
                          config: MainConfig,
                          sheets_controller: SheetsController) -> Router:

    start_end_router.message.middleware(ConfigMiddleware(config))
    start_end_router.message.middleware(DatabaseMiddleware(orm_controller))

    loader_router.message.middleware(StorageMiddleware(storage))
    loader_router.callback_query.middleware(StorageMiddleware(storage))
    loader_router.message.middleware(ConfigMiddleware(config))
    loader_router.callback_query.middleware(ConfigMiddleware(config))
    loader_router.message.middleware(DatabaseMiddleware(orm_controller))
    loader_router.callback_query.middleware(DatabaseMiddleware(orm_controller))
    loader_router.message.middleware(SheetsMiddleware(sheets_controller))
    loader_router.callback_query.middleware(SheetsMiddleware(sheets_controller))
    loader_router.message.middleware(AccessMiddleware(loaders_rights))
    loader_router.callback_query.middleware(AccessMiddleware(loaders_rights))

    packer_router.message.middleware(StorageMiddleware(storage))
    packer_router.callback_query.middleware(StorageMiddleware(storage))
    packer_router.message.middleware(ConfigMiddleware(config))
    packer_router.callback_query.middleware(ConfigMiddleware(config))
    packer_router.message.middleware(DatabaseMiddleware(orm_controller))
    packer_router.callback_query.middleware(DatabaseMiddleware(orm_controller))
    packer_router.message.middleware(SheetsMiddleware(sheets_controller))
    packer_router.callback_query.middleware(SheetsMiddleware(sheets_controller))
    packer_router.message.middleware(AccessMiddleware(packers_rights))
    packer_router.callback_query.middleware(AccessMiddleware(packers_rights))

    admin_router.message.middleware(DatabaseMiddleware(orm_controller))
    admin_router.callback_query.middleware(DatabaseMiddleware(orm_controller))
    admin_router.message.middleware(StorageMiddleware(storage))
    admin_router.callback_query.middleware(StorageMiddleware(storage))
    admin_router.callback_query.middleware(ApschedulerMiddleware(scheduler))
    admin_router.message.middleware(AccessMiddleware(admins_rights))
    admin_router.callback_query.middleware(AccessMiddleware(admins_rights))
    # admin_router.message.filter(ChatAdminFilter(admins_id))
    # admin_router.callback_query.filter(ChatAdminFilter(admins_id))
    admin_router.message.middleware(SheetsMiddleware(sheets_controller))
    admin_router.callback_query.middleware(SheetsMiddleware(sheets_controller))
    admin_router.message.middleware(ConfigMiddleware(config))
    admin_router.callback_query.middleware(ConfigMiddleware(config))

    router: Router = Router()
    router.message.filter(ChatTypeFilter("private"))

    router.include_routers(
        start_end_router, packer_router, admin_router, loader_router
    )
    return router
