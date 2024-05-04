from src.configurations.reading_env import env


class BotConfig:
    def __init__(self):
        self.__token = env("TOKEN")
        self.__developers_id = env.int("DEVELOPER_IDS")
        self.__packers_rights = env.list("PACKERS_RIGHTS")
        self.__managers_rights = env.list("MANAGERS_RIGHTS")
        self.__admins_rights = env.list("ADMINS_RIGHTS")
        self.__loaders_rights = env.list("LOADERS_RIGHTS")
        self.__yandex_disk_token = env.str("YANDEX_DISK_TOKEN")

    def get_token(self) -> str:
        return self.__token

    def get_yandex_disk_token(self) -> str:
        return self.__yandex_disk_token

    def get_developers_id(self) -> int:
        return self.__developers_id

    def get_rights(self, role: str) -> list:
        if role == 'packer':
            return self.__packers_rights
        elif role == 'manager':
            return self.__managers_rights
        elif role == 'loader':
            return self.__loaders_rights
        elif role == 'admin':
            return self.__admins_rights
        else:
            return []
