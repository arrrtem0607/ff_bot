from src.database.entities.models import Good
from src.database.controllers.base_controller import BaseController, session_manager


class GoodController(BaseController):
    @session_manager
    async def insert_good(self, session, sku: int, name: str, technical_task: str, video_url: str):
        new_good = Good(sku=sku, name=name, technical_task=technical_task, video_url=video_url)
        return await self.insert(session, new_good)

    async def delete_good(self, sku: int):
        condition = Good.sku == sku
        return await self.delete(Good, condition)

    async def update_good(self, sku: int, update_data: dict):
        condition = Good.sku == sku
        return await self.update(Good, condition, update_data)

    async def select_good(self, sku: int):
        condition = Good.sku == sku
        goods = await self.select(Good, condition)
        return goods[0] if goods else None

    async def good_exists(self, sku: int):
        condition = Good.sku == sku
        return await self.exists(Good, condition)

    async def count_goods(self):
        return await self.count(Good)
