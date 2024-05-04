from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import callback_query
from datetime import datetime
import logging

from src.bot.keyboards.inline import InlineKeyboards
from src.bot.utils.statesform import Loading
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController


router = Router()
logger = logging.getLogger(__name__)


# ___________________________
# Функция для учета времени погрузки и разгрузки
@router.callback_query(F.data == 'start_loading')
async def loading(callback: callback_query, state: FSMContext):
    logger.info(f"Сотрудник {callback.from_user.first_name} ушел на погрузку")
    start_loading_time = datetime.now().isoformat()
    reply_markup = InlineKeyboards().end_loading()
    await callback.message.edit_text(text='Время погрузки/разгрузки товара засечено, '
                                          'не забудьте отметиться после того, как закончите',
                                     reply_markup=reply_markup)
    await state.update_data(start_loading_time=start_loading_time)
    await state.set_state(Loading.OnLoading)


@router.callback_query(F.data == 'end_loading', Loading.OnLoading)
async def end_loading(callback: callback_query,
                      state: FSMContext,
                      db_controller: ORMController,
                      sheets_controller: SheetsController):
    logger.info(f"Сотрудник {callback.from_user.first_name} вернулся с погрузки")
    end_loading_time = datetime.now()
    load_data = await state.get_data()
    start_loading_time = datetime.fromisoformat(load_data.get('start_loading_time'))
    duration = (end_loading_time - start_loading_time).total_seconds()
    tg_id = callback.message.chat.id

    await db_controller.add_loading_info(tg_id=tg_id,
                                         start_time=start_loading_time,
                                         end_time=end_loading_time,
                                         duration=duration)
    logger.info('Добавил информацию в БД')
    try:
        await sheets_controller.add_loading_info_to_sheet(tg_id=tg_id,
                                                          username=(callback.from_user.first_name or None),
                                                          start_time=start_loading_time,
                                                          end_time=end_loading_time,
                                                          duration=duration)
        logger.info('Добавил информацию в таблицы')
    except Exception as e:
        logger.info(f'Произошла ошибка при добавлении информации в таблицы: {e} ')

    await state.clear()
    role = await db_controller.get_user_role(callback.from_user.id)
    await callback.message.edit_text(text='Погрузка/разгрузка завершена, продолжайте работу',
                                     reply_markup=InlineKeyboards().menu(role=role))
