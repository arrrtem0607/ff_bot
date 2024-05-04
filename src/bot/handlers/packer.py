from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, callback_query
from datetime import datetime
import logging

from src.bot.keyboards.inline import InlineKeyboards
from src.bot.utils.statesform import Packing
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController

router: Router = Router()
logger = logging.getLogger(__name__)


# Функции отслеживания время упаковки
@router.callback_query(F.data == 'start_packing')
async def start_to_pack(message: Message, bot: Bot, state: FSMContext):

    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите артикул с этикетки, которую Вам выдали')
    await state.set_state(Packing.PRODUCT_SELECTION)


@router.message(F.text, Packing.PRODUCT_SELECTION)
async def pack_products(message: Message, bot: Bot, state: FSMContext, db_controller: ORMController):
    try:
        sku = int(message.text)
    except ValueError:
        await bot.send_message(chat_id=message.chat.id,
                               text='SKU должен быть числом')
        return

    good = await db_controller.get_good_attribute_by_sku(sku=sku,
                                                         attribute_name='sku')
    # video_url = await db_controller.get_good_attribute_by_sku(sku=sku,attribute_name='video_url')

    technical_task = await db_controller.get_good_attribute_by_sku(sku=sku,
                                                                   attribute_name='technical_task')
    if good:

        await state.update_data(sku=sku)
        await state.update_data(good=good)
        await bot.send_message(chat_id=message.chat.id,
                               text=f'Время упаковки засечено. '
                                    f'Не забывайте отмечаться в конце упаковки. '
                                    f'Для этого необходимо нажать на кнопку '
                                    f'под этим сообщением. '
                                    f'Очень важно следовать техническому заданию. '
                                    f'Кстати, вот и оно: {technical_task}',
                               reply_markup=InlineKeyboards().end_packing())

        '''
        if video_url:
            await bot.send_video(chat_id=message.chat.id, video=video_url)
        '''

        await state.update_data(start_packing_time=datetime.now().isoformat())
        logger.info(f"Сотрудник {message.from_user.name} принялся за упаковку {good}")
        await state.set_state(Packing.PACKING_TIME)

    else:
        await message.answer(text="Товар с таким SKU не найден. Введите корректный артикул")


@router.callback_query(F.data == 'end_packing', Packing.PACKING_TIME)
async def end_packing(callback: callback_query, state: FSMContext):
    await callback.message.edit_text(text='Время упаковки закончено. Введите количество упакованного товара')
    await state.update_data(end_packing_time=datetime.now().isoformat())
    await state.set_state(Packing.REPORT_PACKING_INFO)


@router.message(F.text, Packing.REPORT_PACKING_INFO)
async def report_packing(message: Message,
                         bot: Bot,
                         state: FSMContext,
                         db_controller: ORMController,
                         sh_controller: SheetsController):
    try:
        quantity_packing = int(message.text)
    except ValueError:
        await bot.send_message(chat_id=message.chat.id,
                               text='Количество должно быть числом')
        logger.info(f"Сотрудник {message.from_user.name} неправильно ввел упаковку")
        return

    packing_info = await state.get_data()

    sku = packing_info.get('sku')
    start_time = datetime.fromisoformat(packing_info.get('start_packing_time'))
    end_time = datetime.fromisoformat(packing_info.get('end_packing_time'))
    good = packing_info.get('good')

    await state.clear()

    duration = (end_time - start_time).total_seconds()
    performance = duration / quantity_packing
    performance = round(performance, 2)
    tg_id = message.from_user.id
    role = await db_controller.get_user_role(tg_id=tg_id)

    logger.info(f"Сотрудник {message.from_user.name} закончил за упаковку {good}")

    await bot.send_message(chat_id=message.chat.id,
                           text=f'Отличная работа, ты упаковал {quantity_packing} {good} всего за {duration} секунд. '
                                f'Твоя производительность составила {performance} {good} в секунду',
                           reply_markup=InlineKeyboards().menu(role))
    await db_controller.add_packing_info(sku=sku,
                                         tg_id=tg_id,
                                         start_time=start_time,
                                         end_time=end_time,
                                         duration=duration,
                                         quantity_packing=quantity_packing,
                                         performance=performance)
    try:
        await sh_controller.add_packing_info_to_sheet(sku=sku,
                                                      tg_id=tg_id,
                                                      username=(message.from_user.first_name or None),
                                                      start_time=start_time,
                                                      end_time=end_time,
                                                      duration=duration,
                                                      quantity_packing=quantity_packing,
                                                      performance=performance)
    except Exception as e:
        logger.info(f'Произошла ошибка при добавлении информации в таблицы: {e} ')
