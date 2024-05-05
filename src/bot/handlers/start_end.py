import logging

from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.types import ReplyKeyboardRemove

from src.configurations import MainConfig
from src.bot.keyboards.inline import InlineKeyboards
from src.bot.keyboards.reply import ReplyKeyboards
from src.bot.utils.statesform import Authorization
from src.database.controllers.ORM import ORMController

router = Router()

logger = logging.getLogger(__name__)


@router.startup()
async def notify_start(bot: Bot, config: MainConfig):
    await bot.send_message(config.bot_config.get_developers_id(), "Бот запущен!")


@router.shutdown()
async def stop_bot(bot: Bot,
                   config: MainConfig):
    await bot.send_message(config.bot_config.get_developers_id(), "Бот остановлен!")


@router.message(Command("cancel"))
async def return_to_menu(message: Message,
                         state: FSMContext,
                         db_controller: ORMController):
    await state.clear()
    role = db_controller.get_user_role(message.from_user.id)
    await message.answer(text='Возвращаемся к началу упаковки',
                         reply_markup=InlineKeyboards().menu(role=role))


@router.message(Command("start"))
async def get_start(message: Message,
                    state: FSMContext,
                    authorized: bool,
                    db_controller: ORMController):
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
        role = await db_controller.get_user_role(message.from_user.id)
        await message.answer(text=f"С возвращением, {message.from_user.first_name}! Приятной работы! 🥰",
                             reply_markup=InlineKeyboards().menu(role=role))
        logger.info(f"Приветственное сообщение отправлено пользователю {message.from_user.username}")


@router.message(F.contact, Authorization.GET_CONTACT)
async def get_contact(message: Message, bot: Bot, config: MainConfig, state: FSMContext):
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
        await state.set_state(Authorization.SET_NAME)
    except Exception as e:
        logger.error(f"Ошибка при отправке сообщения администратору: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
