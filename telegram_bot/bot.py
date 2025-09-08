import os
import sys

# --- Настройка Django ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backendAPI.settings")
import django
django.setup()

import asyncio
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

# --- Aiogram ---
from telegram_bot.localization import LANGUAGES
from telegram_bot.utils import get_text
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from api.models import Vacancy
from asgiref.sync import sync_to_async

# --- Модели ---
from userauth.models import TelegramProfile

# --- Загрузка токена ---
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

class Form(StatesGroup):
    waiting_for_token = State()
    waiting_for_add_filter = State()
    waiting_for_del_filter = State()


async def get_user_language_bot(telegram_id):
    """Получаем язык пользователя асинхронно"""
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=telegram_id).first())()
    if profile and profile.language in LANGUAGES:
        return profile.language
    return 'ru'


async def get_main_keyboard(telegram_id):
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=telegram_id).first())()
    """Основная клавиатура с кнопками"""
    lang = await get_user_language_bot(telegram_id)

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Сменить язык" if lang == 'ru' else
                            "🌐 Тилди өзгөртүү" if lang == 'kg' else
                            "🌐 Change language")]
        ],
        resize_keyboard=True
        )
    return keyboard


# --- /start ---
@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.delete()

    args = message.text.split(maxsplit=1)
    token_arg = args[1] if len(args) > 1 else None

    # --- Пришёл с токеном ---
    if token_arg:
        profile = await sync_to_async(lambda: TelegramProfile.objects.filter(token=token_arg).first())()
        if not profile:
            await message.answer("❌ Неверный или устаревший токен.")
            return

        # Проверяем привязку по telegram_id
        if profile.telegram_id:
            if profile.telegram_id == message.from_user.id:
                await message.answer("✅ Этот токен уже привязан к вашему аккаунту.")
            else:
                await message.answer(
                    "❌ Этот токен уже используется другим аккаунтом. "
                    "Сначала отвяжите токен и сгенерируйте новый."
                )
            return

        # Привязываем токен к текущему Telegram
        profile.telegram_id = message.from_user.id
        profile.is_connected = True
        profile.first_name = message.from_user.first_name
        profile.last_name = message.from_user.last_name
        profile.username = message.from_user.username
        await sync_to_async(profile.save)()
        await message.answer(f"✅ Telegram аккаунт успешно подключён, {profile.username}!")
        return

    # --- Просто старт ---
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=message.from_user.id).first())()
    if profile:
        hidden_token = f"{str(profile.token)[:4]}...{str(profile.token)[-4:]}" if profile.token else "нет"
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Оставить токен", callback_data="keep_token")],
                [InlineKeyboardButton(text="🔄 Сменить токен", callback_data="change_token")],
                [InlineKeyboardButton(text="❌ Отвязать токен", callback_data=f"unlink_token:{profile.id}")],
            ]
        )
        sent_message = await message.answer(
            await get_text(message.from_user.id, 'already_linked', token=hidden_token),
            reply_markup=keyboard
        )
        await state.update_data(message_id=sent_message.message_id)
    else:
        sent_message = await message.answer(
            await get_text(message.from_user.id, 'start'),
            reply_markup=await get_main_keyboard(message.from_user.id)
        )
        await state.set_state(Form.waiting_for_token)
        await state.update_data(message_id=sent_message.message_id)


@dp.callback_query(F.data.startswith("unlink_token:"))
async def unlink_token_callback(callback: types.CallbackQuery):
    _, profile_id = callback.data.split(":")
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(id=profile_id).first())()
    if profile:
        old_token = profile.token
        profile.telegram_id = None
        profile.first_name = ""
        profile.last_name = ""
        profile.username = ""
        profile.is_connected = False
        await sync_to_async(profile.save)()
        await callback.message.edit_text(f"❌ Токен отвязан. Старый токен {old_token} больше не действует.")
    else:
        await callback.message.edit_text("⚠️ Ошибка: профиль не найден.")


# --- /help ---
@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.delete()
    await message.answer(await get_text(message.from_user.id, 'help_text'))

# --- /lang ---
@dp.message(Command("lang"))
async def change_language(message: types.Message):
    await message.delete()
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{LANGUAGES['kg']['flag']} Кыргызча", callback_data="lang_kg"),
             InlineKeyboardButton(text=f"{LANGUAGES['ru']['flag']} Русский", callback_data="lang_ru")],
            [InlineKeyboardButton(text=f"{LANGUAGES['en']['flag']} English", callback_data="lang_en")]
        ]
    )
    await message.answer(await get_text(message.from_user.id, 'choose_language'), reply_markup=keyboard)


# --- Обработка кнопок ---
@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery, state: FSMContext):
    # --- Кнопка "Оставить токен" ---
    if callback.data == "keep_token":
        try:
            await callback.message.delete()
        except:
            pass

        profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=callback.from_user.id).first())()
        if profile:
            profile.first_name = callback.from_user.first_name
            profile.last_name = callback.from_user.last_name
            profile.username = callback.from_user.username
            profile.is_connected = True
            await sync_to_async(profile.save)()
            msg_text = await get_text(callback.from_user.id, 'token_kept')
        else:
            msg_text = "⚠️ У вас нет подключённого токена."

        new_keyboard = await get_main_keyboard(callback.from_user.id)
        sent_msg = await callback.message.answer(msg_text, reply_markup=new_keyboard)
        await asyncio.sleep(3)
        await sent_msg.delete()
        await state.clear()

    # --- Кнопка "Сменить токен" ---
    elif callback.data == "change_token":
        try:
            await callback.message.delete()
        except:
            pass

        await callback.message.answer(await get_text(callback.from_user.id, 'enter_new_token'))
        await state.set_state(Form.waiting_for_token)

    # --- Кнопки смены языка ---
    elif callback.data.startswith("lang_"):
        try:
            profile = await sync_to_async(TelegramProfile.objects.get)(telegram_id=callback.from_user.id)
            lang_code = callback.data.split("_")[1]
            profile.language = lang_code
            await sync_to_async(profile.save)()

            # Получаем обновлённую клавиатуру с кнопками фильтров (если подключён аккаунт)
            new_keyboard = await get_main_keyboard(callback.from_user.id)

            await callback.message.answer(
                await get_text(callback.from_user.id, 'language_changed', language=LANGUAGES[lang_code]['name']),
                reply_markup=new_keyboard
            )
        except TelegramProfile.DoesNotExist:
            await callback.message.answer(await get_text(callback.from_user.id, 'not_linked'))

    # --- Кнопка "Отвязать токен" ---
    elif callback.data == "unlink_token":
        try:
            profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=callback.from_user.id).first())()
            if profile:
                profile.telegram_id = None
                profile.first_name = ""
                profile.last_name = ""
                profile.username = ""
                profile.is_connected = False
                await sync_to_async(profile.save)()
                await callback.message.edit_text("❌ Токен успешно отвязан.")
            else:
                await callback.message.edit_text("⚠️ У вас нет подключённого токена.")
        except:
            await callback.message.edit_text("⚠️ Ошибка при отвязке токена.")

@dp.callback_query(lambda c: c.data == "keep_token")
async def keep_token(callback: types.CallbackQuery, state: FSMContext):
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=callback.from_user.id).first())()
    if profile:
        profile.first_name = callback.from_user.first_name
        profile.last_name = callback.from_user.last_name
        profile.username = callback.from_user.username
        profile.is_connected = True
        await sync_to_async(profile.save)()
        await callback.message.edit_text("✅ Профиль обновлён!")
    else:
        await callback.message.edit_text("⚠️ У вас нет подключённого токена.")
    await state.clear()


# --- Привязка аккаунта ---
@dp.message(Form.waiting_for_token)
async def link_account(message: types.Message, state: FSMContext):
    await message.delete()
    token = message.text.strip()
    try:
        profile = await sync_to_async(TelegramProfile.objects.get)(token=token)

        # --- если токен уже привязан ---
        if profile.telegram_id:
            if profile.telegram_id == message.from_user.id:
                await message.answer("✅ Этот токен уже привязан к вашему аккаунту.")
            else:
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="🔗 Отвязать через сайт", url="https://твой_сайт/unlink")],
                        [InlineKeyboardButton(text="❌ Отвязать в боте", callback_data=f"unlink_token:{profile.id}")]
                    ]
                )
                await message.answer(
                    "❌ Этот токен уже используется другим аккаунтом.\n"
                    "Выберите способ отвязки:",
                    reply_markup=keyboard
                )
            await state.clear()
            return   # 🚨 обязательно выходим

        profile.telegram_id = message.from_user.id
        profile.is_connected = True
        profile.first_name = message.from_user.first_name
        profile.last_name = message.from_user.last_name
        profile.username = message.from_user.username
        await sync_to_async(profile.save)()

        await message.answer(
            await get_text(message.from_user.id, 'account_linked', token=token),
            reply_markup=await get_main_keyboard(message.from_user.id)
        )
        await state.clear()
        return   # 🚨 обязательно выходим

    except TelegramProfile.DoesNotExist:
        await message.answer(await get_text(message.from_user.id, 'invalid_token'))
        await state.clear()
        return


# --- Обработка неизвестных команд ---
@dp.message()
async def unknown_command(message: types.Message):
    await message.delete()
    await message.answer(
        f"{await get_text(message.from_user.id, 'unknown_command')}\n"
        "/start, /help, /lang",
        reply_markup=await get_main_keyboard(message.from_user.id)
    )


async def format_vacancy_message(user_id, vacancy, query):
    salary_text = await get_text(user_id, 'salary')
    location_text = await get_text(user_id, 'location')
    view_text = await get_text(user_id, 'view_vacancy_button')

    vacancy_url = f"https://quality-herring-fine.ngrok-free.app/vacancies/{vacancy.id}/"

    return (
        f"🏢 <b>{vacancy.title}</b>\n\n"
        f"💵 {vacancy.salary} {salary_text}\n"
        f"📍 {vacancy.city or location_text}\n"
        f"🕒 {vacancy.get_work_type_display()}\n\n"
        f"{vacancy.description[:200]}...\n\n"
        f"<a href='{vacancy_url}'>{view_text}</a>\n\n"
        f"🔍 #{query.replace(' ', '_')}"
    )


# --- Запуск бота ---
async def main():
    try:
        print("🤖 Бот запущен...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())