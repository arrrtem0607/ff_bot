from aiogram.fsm.state import State, StatesGroup


class Authorization(StatesGroup):
    GET_CONTACT = State()
    SET_NAME = State()
    SET_ROLE = State()


class Packing(StatesGroup):
    PRODUCT_SELECTION = State()
    PACKING_TIME = State()
    REPORT_PACKING_INFO = State()
    REPORT_DEFECT_INFO = State()
    SEND_PHOTO_REPORT = State()


class Loading(StatesGroup):
    OnLoading = State()


class AddNewSku(StatesGroup):
    ADD_SKU = State()
    ADD_NAME = State()
    ADD_DESCRIPTION = State()
    ADD_VIDEO_LINK = State()
    ADD_TO_DB = State()


class UpdateGoods(StatesGroup):
    choosing_sku = State()
    choosing_field_sku = State()
    typing_new_value_sku = State()


class UpdateWorkers(StatesGroup):
    choosing_worker = State()
    choosing_field_worker = State()
    typing_new_value_worker = State()
