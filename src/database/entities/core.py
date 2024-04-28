from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.database.controllers.settings import SettingsController


class Database:
    async_engine: AsyncEngine = create_async_engine(url=SettingsController().get_database_url())
    async_session_factory: async_sessionmaker = async_sessionmaker(async_engine)


class Base(DeclarativeBase):
    pass
