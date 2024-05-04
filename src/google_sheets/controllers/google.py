from gspread_asyncio import AsyncioGspreadSpreadsheet, AsyncioGspreadClient, AsyncioGspreadWorksheet
import datetime

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

    async def add_packing_info_to_sheet(self, sku: int,
                                        good: str,
                                        tg_id: int,
                                        username: str,
                                        start_time: datetime, end_time: datetime,
                                        duration: float, quantity_packing: int,
                                        performance: float,
                                        photo_url: str):
        """Добавляет информацию об упаковке в Google Sheets"""
        row = [sku, good, tg_id, username, start_time.isoformat(), end_time.isoformat(),
               duration, quantity_packing, performance, photo_url]
        await self.__worksheet.append_row(row)

    async def add_loading_info_to_sheet(self, tg_id: int, username: str,
                                        start_time: datetime, end_time: datetime,
                                        duration: float):
        """Добавляет информацию о погрузке в Google Sheets"""
        sku = None
        good = None
        quantity_packing = None
        performance = None
        photo_url = None
        row = [sku, good, tg_id, username, start_time.isoformat(), end_time.isoformat(),
               duration, quantity_packing, performance, photo_url]
        await self.__worksheet.append_row(row)
