from datetime import datetime
import logging
from aiogram import Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, callback_query
from src.bot.keyboards.inline import InlineKeyboards
from src.bot.utils.statesform import Packing
from src.database.controllers.ORM import ORMController

router: Router = Router()

logger = logging.getLogger(__name__)

'''
@router.message(Command("start"))
async def get_start(message: Message, state: FSMContext, authorized: bool):
    # Логируем начало обработки команды
    logger.info(f"Обработка команды 'start' для пользователя {message.from_user.username}")

    # Очистка состояния пользователя
    await state.clear()
    logger.info(f"Состояние для пользователя {message.from_user.username} очищено")

    if not authorized:
        # Пользователь не авторизован, запрашиваем номер телефона
        logger.info(f"Пользователь {message.from_user.username} не авторизован. Запрашиваем номер телефона.")
        await message.answer("<b>Привет, я бот фулфилмент-центра! 👋</b>\n"
                             "<i>Для начала работы необходимо авторизоваться. 🔑</i>\n\n"
                             "Пожалуйста, отправьте свой номер телефона следующим сообщением.",
                             reply_markup=ReplyKeyboards().contact_kb())
        await state.set_state(Authorization.GET_CONTACT)
        logger.info(f"Состояние пользователя {message.from_user.username} установлено на GET_CONTACT")
    else:
        # Пользователь авторизован, отправляем приветственное сообщение
        logger.info(f"Пользователь {message.from_user.username} авторизован. Отправляем приветствие.")
        await message.answer(text=f"С возвращением, {message.from_user.first_name}! Приятной работы! 🥰",
                             reply_markup=InlineKeyboards().start_packing())
        logger.info(f"Приветственное сообщение отправлено пользователю {message.from_user.username}")


@router.message(F.contact, Authorization.GET_CONTACT)
async def get_contact(message: Message, bot: Bot, config: MainConfig):
    await message.answer("Отлично! Осталось совсем немного подождать, пока администрация бота одобрит Вашу заявку "
                         "прежде, чем Вы сможете приступить к работе! 📦\n"
                         "<b>Я обязательно пришлю Вам уведомление, когда это произойдёт</b> 😉")
    msg: Message = await message.answer("Чистим за собой клавиатуры...",
                                        reply_markup=ReplyKeyboardRemove())
    await msg.delete()
    tg_id = message.from_user.id
    username = message.from_user.username or "None"
    phone = message.contact.phone_number or "None"
    name = message.contact.first_name or "None"
    try:
        await bot.send_message(config.bot_config.get_developers_id(),
                               "Вам пришла заявка на авторизацию от сотрудника:\n\n"
                               f"Имя (telegram): {message.from_user.first_name}\n"
                               f"Username: {username}\n"
                               f"Номер телефона: {phone}",
                               reply_markup=InlineKeyboards().admin_choice(tg_id=tg_id,
                                                                           username=username,
                                                                           phone=phone,
                                                                           name=name))
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
'''


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
        await state.set_state(Packing.PACKING_TIME)
        stata = await state.get_state()
        logger.info(f'Состояние:{stata}')

    else:
        await message.answer(text="Товар с таким SKU не найден. Введите корректный артикул")


@router.callback_query(F.data == 'end_packing', Packing.PACKING_TIME)
async def end_packing(callback: callback_query, state: FSMContext):
    await callback.message.edit_text(text='Время упаковки закончено. Введите количество упакованного товара')
    await state.update_data(end_packing_time=datetime.now().isoformat())
    await state.set_state(Packing.REPORT_PACKING_INFO)


@router.message(F.text, Packing.REPORT_PACKING_INFO)
async def report_packing(message: Message, bot: Bot, state: FSMContext, db_controller: ORMController):
    print('Я тут')
    logger.info('Я тут')
    try:
        quantity_packing = int(message.text)
    except ValueError:
        await bot.send_message(chat_id=message.chat.id,
                               text='Количество должно быть числом')
        return

    await state.update_data(quantity_packing=quantity_packing)
    packing_info = await state.get_data()

    sku = packing_info.get('sku')
    start_time = datetime.fromisoformat(packing_info.get('start_packing_time'))
    end_time = datetime.fromisoformat(packing_info.get('end_packing_time'))
    quantity_packing = packing_info.get('quantity_packing')

    await state.clear()

    name = await db_controller.get_good_attribute_by_sku(sku=sku,
                                                         attribute_name='name')
    duration = (end_time - start_time).total_seconds()
    performance = duration / quantity_packing
    performance = round(performance, 2)
    username = message.from_user.username or 'None'
    role = db_controller.get_user_role(message.from_user.id)
    await bot.send_message(chat_id=message.chat.id,
                           text=f'Отличная работа, ты упаковал {quantity_packing} {name} всего за {duration} секунд. '
                                f'Твоя производительность составила {performance} {name} в секунду',
                           reply_markup=InlineKeyboards().menu(role))
    await db_controller.add_packing_info(sku=sku,
                                         username=username,
                                         start_time=start_time,
                                         end_time=end_time,
                                         duration=duration,
                                         quantity_packing=quantity_packing,
                                         performance=performance)
