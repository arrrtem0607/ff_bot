from aiogram import Bot, Router
from src.configurations import MainConfig

router = Router()


@router.startup()
async def notify_start(bot: Bot, config: MainConfig):
    await bot.send_message(config.bot_config.get_developers_id(), "Бот запущен!")


@router.shutdown()
async def stop_bot(bot: Bot, config: MainConfig):
    await bot.send_message(config.bot_config.get_developers_id(), "Бот остановлен!")
