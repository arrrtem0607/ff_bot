from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import NoResultFound
import datetime

from src.database.entities.core import Database, Base
from src.database.entities.models import Workers, Goods, PackingInfo


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
                (await session.execute(select(Workers).where(Workers.tg_id == tg_id))).one()
                return True
            except NoResultFound:
                return False
            except Exception as e:
                print(e)

    async def update_worker(self, worker_id: int):
        pass

    async def insert_worker(self, tg_id: int,
                            username: str,
                            phone: str) -> bool:
        new_worker: Workers = Workers(tg_id=tg_id, username=username, phone=phone)
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
                    select(Goods).options(joinedload(Goods.video_url)).filter(Goods.sku == sku)
                )
                good = result.scalars().first()
                if good is None:
                    raise NoResultFound(f"No good found with SKU {sku}")
                return good
            except Exception as e:
                print(f"Unexpected error: {e}")
                return None

    async def add_new_sku(self, sku: int,
                          sku_name: str,
                          sku_technical_task: str,
                          sku_video_link: str):
        # Создаем объект товара
        new_goods = Goods(
            sku=int(sku),
            name=sku_name,
            technical_task=sku_technical_task,
            video_url=sku_video_link
        )

        # Добавление нового товара в базу данных
        async with self.db.async_session_factory() as session:
            async with session.begin():
                session.add(new_goods)
            await session.commit()  # Подтверждение изменений
            return "Товар успешно добавлен."

    async def add_packing_info(self, sku: int,
                               username: str,
                               start_time: datetime,
                               end_time: datetime,
                               duration: float,
                               quantity_packing: int,
                               performance: float):
        async with self.db.async_session_factory() as session:
            async with session.begin():
                new_packing = PackingInfo(
                    sku=sku,
                    username=username,
                    start_time=start_time,
                    end_time=end_time,
                    duration=duration,
                    quantity=quantity_packing,
                    performance=performance
                )
                session.add(new_packing)
                await session.commit()

    async def get_good_attribute_by_sku(self, sku: int, attribute_name: str):
        async with self.db.async_session_factory() as session:
            async with session.begin():
                try:
                    # Проверка на существование атрибута в модели Goods
                    if not hasattr(Goods, attribute_name):
                        raise ValueError(f"Attribute '{attribute_name}' does not exist in Goods model.")

                    # Динамически получаем атрибут модели
                    attribute = getattr(Goods, attribute_name)

                    result = await session.execute(select(attribute).where(Goods.sku == sku))
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
