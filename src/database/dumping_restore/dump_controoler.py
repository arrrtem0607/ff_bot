import subprocess
import logging
from dataclasses import dataclass
import os

from src.configurations.db_config import DatabaseConfig

logger = logging.getLogger(__name__)


@dataclass
class DatabaseDump:
    def __init__(self, db_config: DatabaseConfig):
        self.host: str = db_config.get_db_host()
        self.port: int = db_config.get_db_port()
        self.name: str = db_config.get_db_name()
        self.username: str = db_config.get_db_user()
        self.password: str = db_config.get_db_password()
        self.backup_file: str = db_config.get_db_backup_file()
        self.backup_contents: str = db_config.get_db_backup_contents()


class DatabaseAdapter:
    @staticmethod
    def dump_db(db: DatabaseDump):
        """Создает дамп базы данных."""
        command = (f"PGPASSWORD={db.password} pg_dump -h {db.host} -p {db.port} -U {db.username}"
                   f" -F c -b -v -f {db.backup_file} {db.name}")
        try:
            subprocess.run(command, shell=True, check=True)
            logger.info("Database dump was successfully completed!")
        except subprocess.CalledProcessError as e:
            logger.error(f"Error while trying to dump database: {e}")

    @staticmethod
    def generate_restore_list(backup_file, list_file, filtered_list_file):
        script_content = """#!/bin/bash
pg_restore -l {} > {}
grep -E "TABLE|SEQUENCE" {} > {}
""".format(backup_file, list_file, list_file, filtered_list_file)
        script_path = 'generate_list.sh'
        with open(script_path, 'w') as script_file:
            script_file.write(script_content)

        os.chmod(script_path, 0o755)
        subprocess.run([script_path], check=True)
        os.remove(script_path)  # Удаление скрипта после выполнения

    @staticmethod
    def restore_db(db: DatabaseDump):
        """Восстанавливает базу данных из дампа."""
        # Сначала генерируем список для восстановления
        list_file = 'backup_contents.list'
        filtered_list_file = db.backup_contents
        DatabaseAdapter.generate_restore_list(db.backup_file, list_file, filtered_list_file)

        # Теперь выполняем восстановление
        command = (f"PGPASSWORD={db.password} pg_restore --data-only -L {filtered_list_file} -h {db.host} -p {db.port} "
                   f"-U {db.username} -d {db.name} -v {db.backup_file}")
        try:
            subprocess.run(command, shell=True, check=True)
            logger.info("Database has been restored successfully!")
        except subprocess.CalledProcessError as e:
            logger.error(f"An error occurred while restoring the database: {e}")
