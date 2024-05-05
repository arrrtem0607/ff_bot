from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, callback_query

from datetime import datetime
import logging

from src.bot.keyboards.inline import InlineKeyboards
from src.bot.utils.statesform import Packing
from src.database.controllers.ORM import ORMController
from src.google_sheets.controllers.google import SheetsController
from src.bot.utils.some_other_funcs import upload_file_to_yandex_disk
from src.configurations import get_config

router: Router = Router()
logger = logging.getLogger(__name__)
config = get_config()


# Функции отслеживания время упаковки
@router.callback_query(F.data == 'start_packing')
async def start_to_pack(message: Message,
                        bot: Bot,
                        state: FSMContext):

    await bot.send_message(chat_id=message.from_user.id,
                           text='Введите артикул с этикетки, которую Вам выдали')
    await state.set_state(Packing.PRODUCT_SELECTION)


@router.message(F.text, Packing.PRODUCT_SELECTION)
async def pack_products(message: Message,
                        bot: Bot,
                        state: FSMContext,
                        db_controller: ORMController):
    try:
        sku = int(message.text)
    except ValueError:
        await bot.send_message(chat_id=message.chat.id,
                               text='SKU должен быть числом')
        return

    good = await db_controller.get_good_attribute_by_sku(sku=sku,
                                                         attribute_name='name')
    # video_url = await db_controller.get_good_attribute_by_sku(sku=sku,attribute_name='video_url')

    technical_task = await db_controller.get_good_attribute_by_sku(sku=sku,
                                                                   attribute_name='technical_task')
    if good:

        await state.update_data(sku=sku, good=good)
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
        logger.info(f"Сотрудник {message.from_user.first_name} принялся за упаковку {good}")
        await state.set_state(Packing.PACKING_TIME)

    else:
        await message.answer(text="Товар с таким SKU не найден. Введите корректный артикул")


@router.callback_query(F.data == 'end_packing', Packing.PACKING_TIME)
async def end_packing(callback: callback_query,
                      state: FSMContext):
    await callback.message.edit_text(text='Время упаковки закончено.\n\n'
                                          'Введите количество упакованного товара. '
                                          'Бракованный товар не считается')
    await state.set_state(Packing.REPORT_PACKING_INFO)


@router.message(F.text, Packing.REPORT_PACKING_INFO)
async def report_quantity_info(message: Message,
                               state: FSMContext):
    try:
        quantity_packing = int(message.text)
    except ValueError:
        await message.answer(text='Количество должно быть числом')
        logger.info(f"Сотрудник {message.from_user.first_name} неправильно ввел количество упакованного товара")
        return

    await state.update_data(quantity_packing=quantity_packing)
    await state.set_state(Packing.REPORT_DEFECT_INFO)
    await message.answer('Спасибо, теперь напишите количество выявленного брака')


@router.message(F.text, Packing.REPORT_DEFECT_INFO)
async def report_defect_info(message: Message,
                             state: FSMContext):
    try:
        quantity_defect = int(message.text)
    except ValueError:
        await message.answer(text='Количество должно быть числом')
        logger.info(f"Сотрудник {message.from_user.first_name} неправильно ввел количество брака")
        return

    await state.update_data(quantity_defect=quantity_defect)
    await state.set_state(Packing.SEND_PHOTO_REPORT)
    await message.answer('Отлично, осталось отправить фотоотчет выполненной работы. Сфотографируйте и отправьте')


@router.message(F.photo, Packing.SEND_PHOTO_REPORT)
async def send_report_to_db(message: Message,
                            state: FSMContext,
                            bot: Bot,
                            db_controller: ORMController,
                            sheets_controller: SheetsController):
    end_time = datetime.now()
    photo = message.photo[-1]
    photo_id = photo.file_id
    file = await bot.get_file(photo_id)
    file_path = file.file_path

    packing_info = await state.get_data()

    sku = packing_info.get('sku')
    start_time = datetime.fromisoformat(packing_info.get('start_packing_time'))
    good = packing_info.get('good')
    quantity_packing = packing_info.get('quantity_packing')
    quantity_defect = packing_info.get('quantity_defect')
    await bot.download_file(file_path=file_path,
                            destination=f'Упаковщик:{message.from_user.first_name}, SKU:{sku}, время:{end_time}.jpg')

    await state.clear()

    duration = (end_time - start_time).total_seconds()
    performance = duration / quantity_packing
    performance = round(performance, 2)
    tg_id = message.from_user.id
    role = await db_controller.get_user_role(tg_id=tg_id)
    photo_url = await upload_file_to_yandex_disk(file_path=f'Упаковщик:{message.from_user.first_name}, '
                                                           f'SKU:{sku}, время:{end_time}.jpg',
                                                 token=config.bot_config.get_yandex_disk_token())

    logger.info(f"Сотрудник {message.from_user.first_name} закончил за упаковку {good}")

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
                                         performance=performance,
                                         quantity_defect=quantity_defect,
                                         photo_url=photo_url)
    try:
        await sheets_controller.add_packing_info_to_sheet(sku=sku,
                                                          good=good,
                                                          tg_id=tg_id,
                                                          username=(message.from_user.first_name or None),
                                                          start_time=start_time,
                                                          end_time=end_time,
                                                          duration=duration,
                                                          quantity_packing=quantity_packing,
                                                          performance=performance,
                                                          defect=quantity_defect,
                                                          photo_url=photo_url)
    except Exception as e:
        logger.info(f'Произошла ошибка при добавлении информации в таблицы: {e} ')
