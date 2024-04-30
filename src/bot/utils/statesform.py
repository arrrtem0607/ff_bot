from aiogram.fsm.state import State, StatesGroup


class Authorization(StatesGroup):
    GET_CONTACT = State()


class Packing(StatesGroup):
    PRODUCT_SELECTION = State()
    PACKING_TIME = State()
    REPORT_PACKING_INFO = State()


class AddNewSku(StatesGroup):
    ADD_SKU = State()
    ADD_NAME = State()
    ADD_DESCRIPTION = State()
    ADD_VIDEO_LINK = State()
    ADD_TO_DB = State()


class UpdateGoods(StatesGroup):
    choosing_sku = State()
    choosing_field = State()
    typing_new_value = State()
