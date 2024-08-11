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


class Registration(StatesGroup):
    get_first_name = State()
    get_second_name = State()
    get_birth_date = State()
    get_number = State()
    get_payment_details = State()
    get_bank_name = State()
    review_data = State()
    awaiting_approval = State()


class AdminRegistration(StatesGroup):
    review_application = State()
    select_role = State()
    enter_salary = State()


class MainMenu(StatesGroup):
    main = State()


class ChangeData(StatesGroup):
    change_first_name = State()
    change_second_name = State()
    change_number = State()
    change_payment_details = State()
    change_bank_name = State()


class PackingProcess(StatesGroup):
    product_selection = State()
    pacing_time = State()
    report_packing_info = State()
    report_defect_info = State()
    send_photo_report = State()


class Statistics(StatesGroup):
    start = State()
