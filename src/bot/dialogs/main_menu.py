from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Group, Row
from aiogram_dialog.widgets.text import Const
from src.bot.utils.statesform import MainMenu, ChangeData, PackingProcess, Statistics


async def get_role(dialog_manager: DialogManager, **kwargs):
    role = dialog_manager.current_context().dialog_data.get("role")
    return {"role": role}


async def on_role_select(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    role = button.widget_id
    dialog_manager.current_context().dialog_data["role"] = role
    await dialog_manager.switch_to(MainMenu.main)


async def navigate_to_change_data(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(ChangeData.change_first_name)


async def navigate_to_packing_process(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(PackingProcess.product_selection)


async def navigate_to_statistics(c: CallbackQuery, button: Button, dialog_manager: DialogManager):
    await dialog_manager.start(Statistics.start)


main_menu_dialog = Dialog(
    Window(
        Const("Главное меню"),
        Group(
            Row(
                Button(Const("Изменить данные"), id="change_data", on_click=navigate_to_change_data),
                Button(Const("Процесс упаковки"), id="packing_process", on_click=navigate_to_packing_process),
                Button(Const("Статистика"), id="statistics", on_click=navigate_to_statistics),
            ),
        ),
        state=MainMenu.main,
    )
)
