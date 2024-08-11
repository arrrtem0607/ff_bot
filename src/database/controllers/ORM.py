from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import logging
from functools import wraps

from src.database.entities.core import Database, Base
from src.database.entities.models import Worker, Good, PackingInfo, ProductBalance
from src.configurations import get_config

# Настройка логирования
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - [%(levelname)s] - %(name)s - '
                           '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
                    handlers=[
                        logging.FileHandler("application.log"),
                        logging.StreamHandler()
                    ])

logger = logging.getLogger(__name__)
config = get_config()


def session_manager(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        async with self.db.async_session_factory() as session:
            try:
                return await func(self, session, *args, **kwargs)
            except Exception as e:
                await session.rollback()
                logger.error(f"Ошибка в {func.__name__}: {e}")
                raise e
    return wrapper


class ORMController:
    def __init__(self, db: Database = Database()):
        self.db = db

    async def create_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @session_manager
    async def check_worker(self, session, tg_id: int) -> bool:
        try:
            result = await session.execute(select(Worker).where(Worker.tg_id == tg_id))
            worker = result.scalar_one()
            return True
        except NoResultFound:
            return False

    @session_manager
    async def create_worker(self, session, worker_data):
        logger.info(f"Создание сотрудника с данными: {worker_data}")

        # Преобразуем дату рождения обратно в объект date
        worker_data['date_of_birth'] = datetime.strptime(worker_data['date_of_birth'], "%Y-%m-%d").date()

        worker = Worker(**worker_data)
        session.add(worker)
        await session.flush()

        logger.info(f"Сотрудник создан с ID: {worker.id}")
        await session.commit()

        return worker

    @session_manager
    async def get_worker_by_tg_id(self, session: AsyncSession, tg_id: int):
        logger.info(f"Поиск сотрудника с Telegram ID: {tg_id}")
        query = select(Worker).where(Worker.tg_id == tg_id)
        result = await session.execute(query)
        worker = result.scalar_one_or_none()
        return worker

    @session_manager
    async def update_worker_data(self, session, tg_id: int, **kwargs):
        """
        Обновляет данные сотрудника. Передавайте нужные поля и их значения через kwargs.

        :param tg_id: Telegram ID сотрудника.
        :param kwargs: Пары "имя поля" : "значение".
        :return: Обновленный объект Worker.
        """
        if not kwargs:
            raise ValueError("Не указаны поля для обновления")

        logger.info(f"Обновление данных сотрудника с Telegram ID {tg_id}: {kwargs}")
        stmt = update(Worker).where(Worker.tg_id == tg_id).values(**kwargs)
        await session.execute(stmt)
        await session.commit()

        # Получение обновленного сотрудника
        updated_worker = await session.execute(select(Worker).where(Worker.tg_id == tg_id))
        return updated_worker.scalar_one_or_none()
