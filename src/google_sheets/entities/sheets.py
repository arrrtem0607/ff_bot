from datetime import datetime

from google.oauth2.service_account import Credentials
from gspread_asyncio import (
    AsyncioGspreadClient,
    AsyncioGspreadClientManager,
    AsyncioGspreadSpreadsheet,
    AsyncioGspreadWorksheet,
)


class GoogleSheets:
    def __init__(self, connection: AsyncioGspreadClient):
        self.connection = connection


async def get_google_sheets() -> GoogleSheets:
    agc = AsyncioGspreadClientManager(get_credentials)
    gspread_connect: AsyncioGspreadClient = await agc.authorize()
    return GoogleSheets(gspread_connect)


def get_credentials() -> Credentials:
    scope: list = ["https://www.googleapis.com/auth/spreadsheets",
                   'https://www.googleapis.com/auth/drive'
                   ]
    # path: str = "/home/ff_bot/ff_bot/src/google_sheets/credentials.json"
    path: str = "/Users/DlyaNas/Desktop/Proga/PhyBots/Asinc/FF_main/src/google_sheets/credentials.json"
    creds = Credentials.from_service_account_file(filename=path)
    scoped = creds.with_scopes(scope)
    return scoped
