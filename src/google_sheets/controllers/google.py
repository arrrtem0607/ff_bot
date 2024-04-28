from gspread_asyncio import AsyncioGspreadSpreadsheet, AsyncioGspreadClient, AsyncioGspreadWorksheet
from src.configurations import MainConfig
from src.google_sheets.entities.sheets import GoogleSheets


class SheetsController:
    def __init__(self, sheets: GoogleSheets, config: MainConfig):
        self.__config = config
        self.__connection: AsyncioGspreadClient = sheets.connection
        self.__spreadsheet: AsyncioGspreadSpreadsheet | None = None
        self.__worksheet: AsyncioGspreadWorksheet | None = None

    async def set_spreadsheet_and_worksheet(self):
        self.__spreadsheet = await self.__connection.open_by_url(self.__config.sheets_config.get_google_href())
        self.__worksheet: AsyncioGspreadWorksheet = await self.__spreadsheet.get_worksheet(
            self.__config.sheets_config.get_table_num())
