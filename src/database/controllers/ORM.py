from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
import datetime
import logging
from functools import wraps

from src.database.entities.core import Database, Base
from src.database.entities.models import Worker, Good, PackingInfo, ProductBalance
from src.configurations import get_config

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
                logger.error(f"Error in {func.__name__}: {e}")
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
    async def select_from_workers(self, session, worker_id: int | None = None):
        pass

    @session_manager
    async def check_worker(self, session, tg_id: int) -> bool:
        try:
            await session.execute(select(Worker).where(Worker.tg_id == tg_id)).one()
            return True
        except NoResultFound:
            return False

    @session_manager
    async def update_worker(self, session, worker_id: int):
        pass

    @session_manager
    async def insert_worker(self, session, tg_id: int, username: str, phone: str, name: str) -> bool:
        new_worker = Worker(tg_id=tg_id, username=username, phone=phone, name=name)
        session.add(new_worker)
        await session.commit()
        return True

    @session_manager
    async def delete_worker(self, session):
        await session.commit()

    @session_manager
    async def get_good_by_sku(self, session, sku: int):
        try:
            result = await session.execute(select(Good).options(joinedload(Good.video_url)).filter(Good.sku == sku))
            good = result.scalars().first()
            if good is None:
                raise NoResultFound(f"No good found with SKU {sku}")
            return good
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    @session_manager
    async def add_new_sku(self, session, sku: int, sku_name: str, sku_technical_task: str, sku_video_link: str):
        new_goods = Good(sku=sku, name=sku_name, technical_task=sku_technical_task, video_url=sku_video_link)
        existing_goods = await session.get(Good, sku)
        if existing_goods:
            return "Товар с таким SKU уже существует в базе данных."
        session.add(new_goods)
        await session.commit()
        return "Товар успешно добавлен."

    @session_manager
    async def add_packing_info(self, session, sku: int, tg_id: int, start_time: datetime, end_time: datetime, duration: float, quantity_packing: int, performance: float, quantity_defect: int, photo_url: str):
        result = await session.execute(select(Worker.username).where(Worker.tg_id == tg_id))
        username = result.scalar()

        new_packing = PackingInfo(type='packing', sku=sku, username=username, start_time=start_time, end_time=end_time, duration=duration, quantity=quantity_packing, performance=performance, defect=quantity_defect, photo_url=photo_url)
        session.add(new_packing)

        balance = await session.execute(select(ProductBalance).where(ProductBalance.sku == sku))
        balance_obj = balance.scalar_one_or_none()

        if balance_obj:
            balance_obj.defect += quantity_defect
            balance_obj.quantity -= quantity_packing + quantity_defect
        else:
            new_balance = ProductBalance(sku=sku, quantity=0, defect=quantity_defect)
            session.add(new_balance)

        await session.commit()

    @session_manager
    async def add_loading_info(self, session, tg_id: int, start_time: datetime, end_time: datetime, duration: float):
        result = await session.execute(select(Worker.username).where(Worker.tg_id == tg_id))
        username = result.scalar()

        new_loading = PackingInfo(type='loading', username=username, start_time=start_time, end_time=end_time, duration=duration)
        session.add(new_loading)
        await session.commit()

    @session_manager
    async def get_good_attribute_by_sku(self, session, sku: int, attribute_name: str):
        try:
            if not hasattr(Good, attribute_name):
                raise ValueError(f"Attribute '{attribute_name}' does not exist in Good model.")
            attribute = getattr(Good, attribute_name)
            result = await session.execute(select(attribute).where(Good.sku == sku))
            attribute_value = result.scalars().first()
            if attribute_value is None:
                raise NoResultFound(f"No good found with SKU {sku} or attribute '{attribute_name}' is empty.")
            return attribute_value
        except Exception as e:
            logger.error(f"Error: {e}")
            return None

    @session_manager
    async def get_all_goods(self, session):
        result = await session.execute(select(Good))
        return result.scalars().all()

    @session_manager
    async def get_all_workers(self, session):
        result = await session.execute(select(Worker))
        return result.scalars().all()

    @session_manager
    async def change_data_sku(self, session, sku: int, field: str, value: str):
        stmt = update(Good).where(Good.sku == sku).values({field: value})
        await session.execute(stmt)
        await session.commit()

    @session_manager
    async def change_data_worker(self, session, worker_name: str, field: str, value: str):
        stmt = update(Worker).where(Worker.name == worker_name).values({field: value})
        await session.execute(stmt)
        await session.commit()

    @session_manager
    async def get_user_role(self, session, tg_id):
        result = await session.execute(select(Worker.role).where(Worker.tg_id == tg_id))
        role_record = result.scalars().first()
        admins_id = config.bot_config.get_developers_id()
        if tg_id == admins_id:
            role_record = 'packer'
        return role_record or "guest"

    @session_manager
    async def set_worker_name(self, session, name, tg_id):
        stmt = update(Worker).where(Worker.tg_id == tg_id).values(name=name)
        await session.execute(stmt)
        await session.commit()
