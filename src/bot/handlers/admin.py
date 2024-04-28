from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.types import Message, callback_query
from aiogram.fsm.context import FSMContext
from src.bot.utils.statesform import AddNewSku
from src.bot.utils.callbackfabric import AcceptChoice
from src.database.controllers.ORM import ORMController
from src.bot.keyboards.inline import InlineKeyboards

router: Router = Router()


@router.message(Command('menu'))
async def menu(message: Message):
    await message.answer(text='Выберете действие', reply_markup=InlineKeyboards().admin_menu())


@router.callback_query(AcceptChoice.filter())
async def accept(callback: callback_query, callback_data: AcceptChoice, db_controller: ORMController,
                 bot: Bot):
    if callback_data.accept:
        status: bool = await db_controller.insert_worker(tg_id=callback_data.tg_id,
                                                         username=callback_data.username,
                                                         phone=callback_data.phone)
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

    await db_controller.add_new_sku(sku=sku,
                                    sku_name=sku_name,
                                    sku_technical_task=sku_technical_task,
                                    sku_video_link=sku_video_link)

    await bot.send_message(chat_id=message.chat.id,
                           text=f'Товар {sku_name} успешно добавлен в базу данных, продолжайте работу',
                           reply_markup=InlineKeyboards().admin_menu())
    await state.clear()
