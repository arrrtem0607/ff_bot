from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
import datetime
import logging

from src.database.entities.core import Database, Base
from src.database.entities.models import Worker, Good, PackingInfo
from src.configurations import get_config

logger = logging.getLogger(__name__)
config = get_config()


class ORMController:
    def __init__(self, db: Database = Database()):
        self.db = db

    async def create_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def select_from_workers(self, worker_id: int | None = None):
        pass

    async def check_worker(self, tg_id: int) -> bool:
        async with self.db.async_session_factory() as session:
            try:
                (await session.execute(select(Worker).where(Worker.tg_id == tg_id))).one()
                return True
            except NoResultFound:
                return False
            except Exception as e:
                print(e)

    async def update_worker(self, worker_id: int):
        pass

    async def insert_worker(self, tg_id: int,
                            username: str,
                            phone: str,
                            name: str) -> bool:
        new_worker: Worker = Worker(tg_id=tg_id,
                                    username=username,
                                    phone=phone,
                                    name=name)
        exec_code: bool = True
        async with self.db.async_session_factory() as session:
            try:
                session.add(new_worker)
                await session.commit()
                return exec_code
            except Exception as e:
                print(e)
                exec_code = False
                return exec_code

    async def delete_worker(self):
        async with self.db.async_session_factory() as session:
            await session.commit()

    async def get_good_by_sku(self, sku: int):
        async with self.db.async_session_factory() as session:
            try:
                result = await session.execute(
                    select(Good).options(joinedload(Good.video_url)).filter(Good.sku == sku)
                )
                good = result.scalars().first()
                if good is None:
                    raise NoResultFound(f"No good found with SKU {sku}")
                return good
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

    async def add_new_sku(self, sku: int, sku_name: str, sku_technical_task: str, sku_video_link: str):
        new_goods = Good(
            sku=sku,
            name=sku_name,
            technical_task=sku_technical_task,
            video_url=sku_video_link
        )

        async with self.db.async_session_factory() as session:
            try:
                existing_goods = await session.get(Good, sku)
                if existing_goods:
                    return "Товар с таким SKU уже существует в базе данных."
                else:
                    session.add(new_goods)
                    text = "Товар успешно добавлен."

                await session.commit()
                return text

            except Exception as e:
                await session.rollback()
                raise e

    async def add_packing_info(self, sku: int,
                               tg_id: int,
                               start_time: datetime,
                               end_time: datetime,
                               duration: float,
                               quantity_packing: int,
                               performance: float,
                               quantity_defect: int,
                               photo_url: str):
        async with self.db.async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Worker.username).where(Worker.tg_id == tg_id)
                )
                username = result.scalar()

                try:
                    new_packing = PackingInfo(
                        sku=sku,
                        username=username,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                        quantity=quantity_packing,
                        performance=performance,
                        defect=quantity_defect,
                        photo_url=photo_url
                    )
                    session.add(new_packing)
                    await session.commit()
                except Exception as e:
                    print(f"Ошибка при добавлении данных: {e}")

    async def add_loading_info(self, tg_id: int,
                               start_time: datetime,
                               end_time: datetime,
                               duration: float):
        async with self.db.async_session_factory() as session:
            async with session.begin():
                result = await session.execute(
                    select(Worker.username).where(Worker.tg_id == tg_id)
                )
                username = result.scalar()

                try:
                    new_loading = PackingInfo(
                        username=username,
                        start_time=start_time,
                        end_time=end_time,
                        duration=duration,
                    )
                    session.add(new_loading)
                    await session.commit()
                except Exception as e:
                    print(f"Ошибка при добавлении информации о загрузке: {e}")

    async def get_good_attribute_by_sku(self, sku: int, attribute_name: str):
        async with self.db.async_session_factory() as session:
            async with session.begin():
                try:
                    # Проверка на существование атрибута в модели Good
                    if not hasattr(Good, attribute_name):
                        raise ValueError(f"Attribute '{attribute_name}' does not exist in Good model.")

                    # Динамически получаем атрибут модели
                    attribute = getattr(Good, attribute_name)

                    result = await session.execute(select(attribute).where(Good.sku == sku))
                    attribute_value = result.scalars().first()

                    if attribute_value is None:
                        raise NoResultFound(f"No good found with SKU {sku} or attribute '{attribute_name}' is empty.")

                    return attribute_value
                except NoResultFound as e:
                    print(f"Error: {e}")
                    return None
                except ValueError as e:
                    print(f"Error: {e}")
                    return None
                except Exception as e:
                    print(f"Unexpected error: {e}")
                    return None

    async def get_all_goods(self):
        async with self.db.async_session_factory() as session:
            try:
                result = await session.execute(select(Good))
                goods = result.scalars().all()
                return goods
            except Exception as e:
                print(f"Unexpected error when retrieving goods: {e}")
                return None

    async def get_all_workers(self):
        async with self.db.async_session_factory() as session:
            try:
                result = await session.execute(select(Worker))
                workers = result.scalars().all()
                return workers
            except Exception as e:
                print(f"Unexpected error when retrieving goods: {e}")
                return None

    async def change_data_sku(self, sku: int, field: str, value: str):
        async with self.db.async_session_factory() as session:

            stmt = update(Good).where(Good.sku == int(sku)).values({field: value})

            await session.execute(stmt)

            await session.commit()

    async def change_data_worker(self, worker_name: str, field: str, value: str):
        async with self.db.async_session_factory() as session:

            stmt = update(Worker).where(Worker.name == worker_name).values({field: value})

            await session.execute(stmt)

            await session.commit()

    async def get_user_role(self, tg_id):
        async with self.db.async_session_factory() as session:
            result = await session.execute(
                select(Worker.role).where(Worker.tg_id == tg_id)
            )
            role_record = result.scalars().first()
            admins_id: int = config.bot_config.get_developers_id()
            if tg_id == admins_id:
                role_record = 'loader'
            return role_record or "guest"

    async def set_worker_name(self, name, tg_id):
        async with self.db.async_session_factory() as session:
            stmt = update(Worker).where(Worker.tg_id == tg_id).values(name=name)
            await session.execute(stmt)
            await session.commit()

    async def update_packing_info_with_photo(self, packing_id: int, photo_url: str):
        """
        Обновляет запись об упаковке, добавляя URL фотографии.

        :param packing_id: ID записи об упаковке
        :param photo_url: URL фотографии для сохранения
        """
        async with self.db.async_session_factory() as session:
            stmt = update(PackingInfo).where(PackingInfo.id == packing_id).values(photo_url=photo_url)
            await session.execute(stmt)
            await session.commit()
