from src.configurations.reading_env import env


class SheetsConfig:
    def __init__(self):
        self.__href = env("GOOGLE_HREF")
        self.__table_num = env.int("TABLE_NUM")

    def get_google_href(self) -> str:
        return self.__href

    def get_table_num(self) -> int:
        return self.__table_num
