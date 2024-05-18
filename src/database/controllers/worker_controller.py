from src.database.entities.models import Worker
from src.database.controllers.base_controller import BaseController, session_manager


class WorkerController(BaseController):
    @session_manager
    async def insert_worker(self, session, tg_id: int, username: str, phone: str, name: str):
        new_worker = Worker(tg_id=tg_id, username=username, phone=phone, name=name)
        return await self.insert(session, new_worker)

    async def delete_worker(self, worker_id: int):
        condition = Worker.id == worker_id
        return await self.delete(Worker, condition)

    async def update_worker(self, worker_id: int, update_data: dict):
        condition = Worker.id == worker_id
        return await self.update(Worker, condition, update_data)

    async def select_worker(self, tg_id: int):
        condition = Worker.tg_id == tg_id
        workers = await self.select(Worker, condition)
        return workers[0] if workers else None

    async def worker_exists(self, tg_id: int):
        condition = Worker.tg_id == tg_id
        return await self.exists(Worker, condition)

    async def count_workers(self):
        return await self.count(Worker)
