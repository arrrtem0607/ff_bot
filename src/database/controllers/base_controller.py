from sqlalchemy import select, update, delete, func as sqlalchemy_func
from sqlalchemy.exc import NoResultFound
import logging
from functools import wraps
import asyncio
import os

logger = logging.getLogger(__name__)


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


class DatabaseDump:
    def __init__(self, db_config):
        self.host = db_config.get_db_host()
        self.port = db_config.get_db_port()
        self.name = db_config.get_db_name()
        self.username = db_config.get_db_user()
        self.password = db_config.get_db_password()
        self.backup_file = db_config.get_db_backup_file()
        self.backup_contents = db_config.get_db_backup_contents()


class BaseController:
    def __init__(self, db):
        self.db = db

    async def create_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(self.db.Base.metadata.create_all)

    async def drop_tables(self):
        async with self.db.async_engine.begin() as conn:
            await conn.run_sync(self.db.Base.metadata.drop_all)

    async def dump_db(self, db: DatabaseDump):
        """Создает дамп базы данных."""
        command = (f"PGPASSWORD={db.password} pg_dump -h {db.host} -p {db.port} -U {db.username}"
                   f" -F c -b -v -f {db.backup_file} {db.name}")
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info("Database dump was successfully completed!")
            else:
                logger.error(f"Error while trying to dump database: {stderr.decode()}")
        except Exception as e:
            logger.error(f"Error while trying to dump database: {e}")

    async def generate_restore_list(self, backup_file, list_file, filtered_list_file):
        script_content = f"""#!/bin/bash
pg_restore -l {backup_file} > {list_file}
grep -E "TABLE|SEQUENCE" {list_file} > {filtered_list_file}
"""
        script_path = 'generate_list.sh'
        with open(script_path, 'w') as script_file:
            script_file.write(script_content)

        os.chmod(script_path, 0o755)
        process = await asyncio.create_subprocess_shell(
            f"./{script_path}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await process.communicate()
        if process.returncode == 0:
            logger.info("Restore list was successfully generated!")
        else:
            logger.error(f"Error while generating restore list: {stderr.decode()}")
        os.remove(script_path)  # Удаление скрипта после выполнения

    async def restore_db(self, db: DatabaseDump):
        """Восстанавливает базу данных из дампа."""
        list_file = 'backup_contents.list'
        filtered_list_file = db.backup_contents
        await self.generate_restore_list(db.backup_file, list_file, filtered_list_file)

        command = (f"PGPASSWORD={db.password} pg_restore --data-only -L {filtered_list_file} -h {db.host} -p {db.port} "
                   f"-U {db.username} -d {db.name} -v {db.backup_file}")
        try:
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            if process.returncode == 0:
                logger.info("Database has been restored successfully!")
            else:
                logger.error(f"An error occurred while restoring the database: {stderr.decode()}")
        except Exception as e:
            logger.error(f"An error occurred while restoring the database: {e}")

    @session_manager
    async def insert(self, session, model_instance):
        try:
            session.add(model_instance)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Insert error: {e}")
            return False

    @session_manager
    async def bulk_insert(self, session, model_instances):
        try:
            session.bulk_save_objects(model_instances)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Bulk insert error: {e}")
            return False

    @session_manager
    async def delete(self, session, model, condition):
        try:
            stmt = delete(model).where(condition)
            await session.execute(stmt)
            await session.commit()
            return True
        except NoResultFound as e:
            logger.error(e)
            return False
        except Exception as e:
            logger.error(f"Delete error: {e}")
            return False

    @session_manager
    async def update(self, session, model, condition, update_data):
        try:
            stmt = update(model).where(condition).values(update_data)
            await session.execute(stmt)
            await session.commit()
            return True
        except Exception as e:
            logger.error(f"Update error: {e}")
            return False

    @session_manager
    async def select(self, session, model, condition=None, options=None):
        try:
            query = select(model)
            if condition:
                query = query.where(condition)
            if options:
                query = query.options(*options)
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Select error: {e}")
            return []

    @session_manager
    async def exists(self, session, model, condition):
        try:
            query = select(sqlalchemy_func.count()).select_from(model).where(condition)
            result = await session.execute(query)
            count = result.scalar()
            return count > 0
        except Exception as e:
            logger.error(f"Exists check error: {e}")
            return False

    @session_manager
    async def count(self, session, model, condition=None):
        try:
            query = select(sqlalchemy_func.count()).select_from(model)
            if condition:
                query = query.where(condition)
            result = await session.execute(query)
            return result.scalar()
        except Exception as e:
            logger.error(f"Count error: {e}")
            return 0

    @session_manager
    async def transaction(self, session, operations):
        try:
            async with session.begin():
                for operation in operations:
                    await operation(session)
            await session.commit()
            return True
        except Exception as e:
            await session.rollback()
            logger.error(f"Transaction error: {e}")
            return False
