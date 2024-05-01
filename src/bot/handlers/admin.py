from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, callback_query
from aiogram.fsm.context import FSMContext
from src.bot.utils.statesform import AddNewSku, UpdateGoods, UpdateWorkers
from src.bot.utils.callbackfabric import AcceptChoice
from src.database.controllers.ORM import ORMController
from src.bot.keyboards.inline import InlineKeyboards

router: Router = Router()


# ____________________________________________________________
# Общие функции
@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer(text='Выберете действие', reply_markup=InlineKeyboards().admin_menu())


@router.callback_query(AcceptChoice.filter())
async def accept(callback: callback_query, callback_data: AcceptChoice, db_controller: ORMController,
                 bot: Bot):
    if callback_data.accept:
        status: bool = await db_controller.insert_worker(tg_id=callback_data.tg_id,
                                                         username=callback_data.username,
                                                         phone=callback_data.phone,
                                                         name=callback_data.name)
        if status:
            await callback.message.edit_text(f"Сотрудник @{callback_data.username} успешно добавлен в базу данных!")
            await bot.send_message(chat_id=callback_data.tg_id,
                                   text="Вы успешно авторизованы в нашем боте! Можете приступать к работе!",
                                   reply_markup=InlineKeyboards().start_packing())
        else:
            await callback.message.edit_text("Произошла непредвиденная ошибка, срочно обратитесь в поддержку бота!")
    else:
        await callback.message.edit_text(text=f"Вы успешно отклонили заявку от человека @{callback_data.username}.")
        await bot.send_message(callback_data.tg_id, "Ваша заявка отклонена администрацией 😭")
# ____________________________________________________________


# ____________________________________________________________
# Функции для добавления товара в базу данных
@router.callback_query(F.data == 'add')
async def add_sku(callback: callback_query, state: FSMContext,):
    await state.set_state(AddNewSku.ADD_SKU)
    await callback.message.edit_text(text='Введите номер SKU')
    await state.set_state(AddNewSku.ADD_NAME)


@router.message(F.text, AddNewSku.ADD_NAME)
async def add_name(message: Message,
                   state: FSMContext,
                   bot: Bot):
    await state.update_data(sku=message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text='Введите название товара')
    await state.set_state(AddNewSku.ADD_DESCRIPTION)


@router.message(F.text, AddNewSku.ADD_DESCRIPTION)
async def add_description(message: Message,
                          state: FSMContext,
                          bot: Bot):
    await state.update_data(sku_name=message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text='Введите техническое задание на упаковку')
    await state.set_state(AddNewSku.ADD_VIDEO_LINK)


@router.message(F.text, AddNewSku.ADD_VIDEO_LINK)
async def add_video(message: Message,
                    state: FSMContext,
                    bot: Bot):
    await state.update_data(sku_technical_task=message.text)
    await bot.send_message(chat_id=message.chat.id,
                           text='Введите ссылку на видео')
    await state.set_state(AddNewSku.ADD_TO_DB)


@router.message(F.text, AddNewSku.ADD_TO_DB)
async def add_info_to_db(message: Message,
                         state: FSMContext,
                         db_controller: ORMController,
                         bot: Bot):

    await state.update_data(video=message.text)
    sku_data = await state.get_data()

    sku = sku_data.get('sku')
    sku_name = sku_data.get('sku_name')
    sku_technical_task = sku_data.get('sku_technical_task')
    sku_video_link = sku_data.get('video')

    result_message = await db_controller.add_new_sku(sku=int(sku),
                                                     sku_name=sku_name,
                                                     sku_technical_task=sku_technical_task,
                                                     sku_video_link=sku_video_link)

    await bot.send_message(chat_id=message.chat.id,
                           text=result_message,
                           reply_markup=InlineKeyboards().admin_menu())
    await state.clear()
# __________________________________________________


# __________________________________________________
# Функции для добавления изменения параметров товара
@router.callback_query(F.data == "change_sku")
async def start_update_sku(callback: callback_query, state: FSMContext, db_controller: ORMController):
    goods = await db_controller.get_all_goods()
    reply_markup = await InlineKeyboards().build_goods_keyboard(goods=goods)
    await callback.message.edit_text(text="Выберите SKU для изменения:",
                                     reply_markup=reply_markup)
    await state.set_state(UpdateGoods.choosing_sku)


@router.callback_query(F.data, UpdateGoods.choosing_sku)
async def choosing_sku_field(callback: callback_query, state: FSMContext):
    sku = callback.data.split('_')[1]
    await state.update_data(sku=sku)
    reply_markup = await InlineKeyboards().choose_sku_field()
    await callback.message.edit_text(text='Выберите поле для замены',
                                     reply_markup=reply_markup)
    await state.set_state(UpdateGoods.choosing_field_sku)


@router.callback_query(F.data, UpdateGoods.choosing_field_sku)
async def typing_new_value_sku(callback: callback_query, state: FSMContext):
    field = callback.data
    await state.update_data(field=field)
    await callback.message.edit_text(text=f'Введите новое значения для поля {field}')
    await state.set_state(UpdateGoods.typing_new_value_sku)


@router.message(F.text, UpdateGoods.typing_new_value_sku)
async def input_new_value_to_db(message: Message, state: FSMContext, db_controller: ORMController, bot: Bot):
    new_data = await state.get_data()
    sku = new_data.get('sku')
    field = new_data.get('field')
    value = message.text
    await bot.send_message(chat_id=message.chat.id,
                           text='Информация изменена, продолжайте работу',
                           reply_markup=InlineKeyboards().admin_menu())
    await db_controller.change_data_sku(sku=sku, field=field, value=value)
# ___________________________________________________


# ___________________________________________________
# Функции для добавления изменения параметров рабочих
@router.callback_query(F.data == "change_worker")
async def start_update_worker(callback: callback_query, state: FSMContext, db_controller: ORMController):
    workers = await db_controller.get_all_workers()
    reply_markup = await InlineKeyboards().build_workers_keyboard(workers=workers)
    await callback.message.edit_text(text="Выберите работника для изменения:",
                                     reply_markup=reply_markup)
    await state.set_state(UpdateWorkers.choosing_worker)


@router.callback_query(F.data, UpdateWorkers.choosing_worker)
async def choosing_worker_field(callback: callback_query, state: FSMContext):
    worker_name = callback.data.split('_')[1]
    await state.update_data(worker_name=worker_name)
    reply_markup = await InlineKeyboards().choose_worker_field()
    await callback.message.edit_text(text='Выберите поле для замены',
                                     reply_markup=reply_markup)
    await state.set_state(UpdateWorkers.choosing_field_worker)


@router.callback_query(F.data, UpdateWorkers.choosing_field_worker)
async def typing_new_value_worker(callback: callback_query, state: FSMContext):
    field = callback.data
    await state.update_data(field=field)
    await callback.message.edit_text(text=f'Введите новое значения для поля {field}')
    await state.set_state(UpdateWorkers.typing_new_value_worker)


@router.message(F.text, UpdateWorkers.typing_new_value_worker)
async def input_new_value_to_db(message: Message, state: FSMContext, db_controller: ORMController, bot: Bot):
    new_data = await state.get_data()
    worker_name = new_data.get('worker_name')
    field = new_data.get('field')
    if field == 'salary':
        value = int(message.text)
    else:
        value = message.text
    await bot.send_message(chat_id=message.chat.id,
                           text='Информация изменена, продолжайте работу',
                           reply_markup=InlineKeyboards().admin_menu())
    await db_controller.change_data_worker(worker_name=worker_name, field=field, value=value)
