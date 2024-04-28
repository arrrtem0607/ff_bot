from aiogram.client.default import DefaultBotProperties
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.bot.handlers import get_all_routers
from src.configurations import get_config
from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import Redis, RedisStorage
import asyncio
import logging
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController
from src.google_sheets.entities.sheets import get_google_sheets


logger = logging.getLogger(__name__)


async def run_bot():
    config = get_config()
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
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s - [%(levelname)s] - %(name)s - "
                               "(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s")
    admins_id: int = config.bot_config.get_developers_id()
    default: DefaultBotProperties = DefaultBotProperties(parse_mode="HTML")
    bot: Bot = Bot(config.bot_config.get_token(), default=default)
    dp: Dispatcher = Dispatcher(storage=storage)
    dp.include_router(await get_all_routers(
        storage=storage,
        admins_id=admins_id,
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