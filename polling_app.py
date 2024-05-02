from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.bot.handlers import get_all_routers
from src.configurations import get_config
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import Redis, RedisStorage
import asyncio
import logging
import os
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
    redis: Redis = Redis(host='localhost')
    storage: RedisStorage = RedisStorage(redis=redis)
    # storage.redis.
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.start()
    orm_controller: ORMController = ORMController()
    # await orm_controller.create_tables()
    # print('Таблицы созданы')
    sheets_controller: SheetsController = SheetsController(await get_google_sheets(), config=config)
    await sheets_controller.set_spreadsheet_and_worksheet()
    admins_id: int = config.bot_config.get_developers_id()
    admins_rights: list = config.bot_config.get_rights('admin')
    loaders_rights: list = config.bot_config.get_rights('loader')
    packers_rights: list = config.bot_config.get_rights('packer')
    managers_rights: list = config.bot_config.get_rights('manager')
    default: DefaultBotProperties = DefaultBotProperties(parse_mode="HTML")
    bot: Bot = Bot(config.bot_config.get_token(), default=default)
    dp: Dispatcher = Dispatcher(storage=storage)
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
    try:
        await dp.start_polling(bot, config=config)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(run_bot())
