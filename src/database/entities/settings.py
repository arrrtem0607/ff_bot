from pydantic_settings import BaseSettings
from src.configurations import MainConfig


class Settings(BaseSettings):
    DB_HOST: str = MainConfig.db_config.get_db_host()
    DB_PORT: int = MainConfig.db_config.get_db_port()
    DB_USER: str = MainConfig.db_config.get_db_user()
    DB_PASS: str = MainConfig.db_config.get_db_password()
    DB_NAME: str = MainConfig.db_config.get_db_name()

