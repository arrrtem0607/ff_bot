from datetime import datetime
import logging
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import callback_query

from src.bot.keyboards.inline import InlineKeyboards
from src.bot.utils.statesform import Loading
from src.database.controllers.ORM import ORMController


router = Router()

logger = logging.getLogger(__name__)


# ___________________________
# Функция для учета времени погрузки и разгрузки
@router.callback_query(F.data == 'start_loading')
async def loading(callback: callback_query, state: FSMContext):
    logger.info(f"Сотрудник {callback.from_user.name} ушел на погрузку")
    start_loading_time = datetime.now().isoformat()
    reply_markup = InlineKeyboards().end_loading()
    await callback.message.edit_text(text='Время погрузки/разгрузки товара засечено, '
                                          'не забудьте отметиться после того, как закончите',
                                     reply_markup=reply_markup)
    await state.update_data(start_loading_time=start_loading_time)
    await state.set_state(Loading.OnLoading)


@router.callback_query(F.data == 'end_loading', Loading.OnLoading)
async def end_loading(callback: callback_query, state: FSMContext, db_controller: ORMController):
    logger.info(f"Сотрудник {callback.from_user.name} вернулся с погрузки")
    end_loading_time = datetime.now()
    load_data = await state.get_data()
    start_loading_time = datetime.fromisoformat(load_data.get('start_loading_time'))
    duration = (end_loading_time - start_loading_time).total_seconds()
    tg_id = callback.message.chat.id

    await db_controller.add_loading_info(tg_id=tg_id,
                                         start_time=start_loading_time,
                                         end_time=end_loading_time,
                                         duration=duration)
    await state.clear()
    role = await db_controller.get_user_role(callback.from_user.id)
    await callback.message.edit_text(text='Погрузка/разгрузка завершена, продолжайте работу',
                                     reply_markup=InlineKeyboards().menu(role=role))
