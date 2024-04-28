from src.configurations.reading_env import env


class BotConfig:
    def __init__(self):
        self.__token = env("TOKEN")
        self.__developers_id = env.int("DEVELOPER_IDS")

    def get_token(self) -> str:
        return self.__token

    def get_developers_id(self) -> int:
        return self.__developers_id
