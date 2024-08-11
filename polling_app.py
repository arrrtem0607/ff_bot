from aiogram.client.default import DefaultBotProperties
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import Redis, RedisStorage, DefaultKeyBuilder
from aiogram_dialog import setup_dialogs

from apscheduler.schedulers.asyncio import AsyncIOScheduler

import asyncio
import logging
import os

from src.bot.dialogs.registration_dialog import registration_dialog
from src.bot.dialogs.main_menu import main_menu_dialog
from src.bot.handlers import get_all_routers
from src.configurations import get_config
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController
from src.google_sheets.entities.sheets import get_google_sheets


logger = logging.getLogger(__name__)
current_directory = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(current_directory, 'application.log')


async def run_bot():
    config = get_config()
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s",
                        filename=log_file_path)
    redis = Redis(host='localhost')
    key_builder = DefaultKeyBuilder(with_destiny=True)
    storage = RedisStorage(redis=redis, key_builder=key_builder)
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    orm_controller = ORMController()
    await orm_controller.create_tables()
    # print('Таблицы созданы')
    sheets_controller = SheetsController(await get_google_sheets(), config=config)
    await sheets_controller.set_spreadsheet_and_worksheet()
    admins_id = config.bot_config.get_developers_id()
    admins_rights = config.bot_config.get_rights('admin')
    loaders_rights = config.bot_config.get_rights('loader')
    packers_rights = config.bot_config.get_rights('packer')
    managers_rights = config.bot_config.get_rights('manager')
    default = DefaultBotProperties(parse_mode="HTML")
    bot = Bot(config.bot_config.get_token(), default=default)
    dp = Dispatcher(storage=storage)

    dp.include_router(await get_all_routers(
        storage=storage,
        admins_id=admins_id,
        admins_rights=admins_rights,
        packers_rights=packers_rights,
        loaders_rights=loaders_rights,
        managers_rights=managers_rights,
        scheduler=scheduler,
        orm_controller=orm_controller,
        sheets_controller=sheets_controller,
        config=config
    )
                      )

    dp.include_router(registration_dialog)
    dp.include_router(main_menu_dialog)
    setup_dialogs(dp)

    try:
        await dp.start_polling(bot, config=config)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run_bot())
