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
from userauth.models import TelegramProfile, CustomUser

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
    """Основная клавиатура с кнопками"""
    lang = await get_user_language_bot(telegram_id)
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="➕ Добавить фильтр" if lang == 'ru' else
                           "➕ Filter кошуу" if lang == 'kg' else
                           "➕ Add filter")],
            [KeyboardButton(text="🗑️ Удалить фильтр" if lang == 'ru' else
                           "🗑️ Filter өчүрүү" if lang == 'kg' else
                           "🗑️ Delete filter"),
             KeyboardButton(text="📋 Мои фильтры" if lang == 'ru' else
                           "📋 Менин фильтрлерим" if lang == 'kg' else
                           "📋 My filters")],
            [KeyboardButton(text="🌐 Сменить язык" if lang == 'ru' else
                           "🌐 Тил өзгөртүү" if lang == 'kg' else
                           "🌐 Change language")]
        ],
        resize_keyboard=True
    )


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

        # Если токен уже привязан к другому телеграм аккаунту
        if profile.telegram_id and profile.telegram_id != message.from_user.id:
            old_id = profile.telegram_id
            profile.telegram_id = message.from_user.id
            profile.is_connected = True
            # Можно уведомить старого юзера через бота, если нужно
        else:
            profile.telegram_id = message.from_user.id
            profile.is_connected = True

        # Обновляем имя, username
        profile.first_name = message.from_user.first_name
        profile.last_name = message.from_user.last_name
        profile.username = message.from_user.username

        # Получаем фото
        photos = await bot.get_user_profile_photos(message.from_user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id
            file = await bot.get_file(file_id)
            profile.avatar_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        else:
            profile.avatar_url = None

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
                [InlineKeyboardButton(text="🔄 Сменить токен", callback_data="change_token")]
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


@dp.callback_query(lambda c: c.data == "unlink_token")
async def unlink_token(callback: types.CallbackQuery):
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=callback.from_user.id).first())()
    if profile:
        profile.telegram_id = None
        profile.is_connected = False
        await sync_to_async(profile.save)()
        await callback.message.edit_text("❌ Токен успешно отвязан.")
    else:
        await callback.message.edit_text("⚠️ У вас нет подключенного токена.")


@dp.callback_query(lambda c: c.data == "keep_token")
async def keep_token(callback: types.CallbackQuery, state: FSMContext):
    # Получаем TelegramProfile текущего пользователя
    profile = await sync_to_async(lambda: TelegramProfile.objects.filter(telegram_id=callback.from_user.id).first())()

    if profile:
        profile.first_name = callback.from_user.first_name
        profile.last_name = callback.from_user.last_name
        profile.username = callback.from_user.username
        profile.is_connected = True

        # Получаем ссылку на фото профиля через Telegram API
        photos = await bot.get_user_profile_photos(callback.from_user.id, limit=1)
        if photos.total_count > 0:
            file_id = photos.photos[0][0].file_id  # берем первую фотографию первого размера
            file = await bot.get_file(file_id)
            profile.avatar_url = f"https://api.telegram.org/file/bot{BOT_TOKEN}/{file.file_path}"
        else:
            profile.avatar_url = None  # фото нет

        await sync_to_async(profile.save)()

        await callback.message.edit_text("✅ Профиль обновлён!")
    else:
        await callback.message.edit_text("⚠️ У вас нет подключённого токена.")

    await state.clear()

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
    if callback.data == "keep_token":
        # Удаляем предыдущее сообщение с кнопками
        try:
            await callback.message.delete()
        except:
            pass

        # Отправляем новое сообщение
        msg = await callback.message.answer(await get_text(callback.from_user.id, 'token_kept'))
        await asyncio.sleep(3)
        await msg.delete()
        await state.clear()

    elif callback.data == "change_token":
        # Удаляем предыдущее сообщение с кнопками
        try:
            await callback.message.delete()
        except:
            pass

        # Отправляем новое сообщение
        await callback.message.answer(await get_text(callback.from_user.id, 'enter_new_token'))
        await state.set_state(Form.waiting_for_token)

    elif callback.data.startswith("lang_"):
        # Удаляем предыдущее сообщение с кнопками выбора языка
        try:
            await callback.message.delete()
        except:
            pass

        lang_code = callback.data.split("_")[1]
        try:
            profile = await sync_to_async(TelegramProfile.objects.get)(telegram_id=callback.from_user.id)
            profile.language = lang_code
            await sync_to_async(profile.save)()
            await callback.message.answer(
                await get_text(callback.from_user.id, 'language_changed', language=LANGUAGES[lang_code]['name'])
            )
        except TelegramProfile.DoesNotExist:
            await callback.message.answer(await get_text(callback.from_user.id, 'not_linked'))
# --- Привязка аккаунта ---
@dp.message(Form.waiting_for_token)
async def link_account(message: types.Message, state: FSMContext):
    token = message.text.strip()
    try:
        profile = await sync_to_async(TelegramProfile.objects.get)(token=token)
        profile.telegram_id = message.from_user.id
        await sync_to_async(profile.save)()
        await message.answer(
            await get_text(message.from_user.id, 'account_linked', token=token),
            reply_markup=await get_main_keyboard(message.from_user.id)
        )
        await state.clear()
        await message.delete()
    except TelegramProfile.DoesNotExist:
        await message.delete()
        await message.answer(await get_text(message.from_user.id, 'invalid_token'))


# --- Добавление фильтра ---
@dp.message(Command("addfilter"))
@dp.message(F.text.contains("➕"))
async def add_filter(message: types.Message, state: FSMContext):
    await message.delete()
    await message.answer(await get_text(message.from_user.id, 'enter_keyword'))
    await state.set_state(Form.waiting_for_add_filter)


@dp.message(Form.waiting_for_add_filter)
async def handle_add_filter(message: types.Message, state: FSMContext):
    text = message.text.strip()
    try:
        profile = await sync_to_async(TelegramProfile.objects.get)(telegram_id=message.from_user.id)

        # Обрабатываем несколько слов через запятую
        keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
        added_keywords = []
        existing_keywords = []

        for keyword in keywords:
            if keyword and keyword not in profile.filters:
                profile.filters.append(keyword)
                added_keywords.append(keyword)
            else:
                existing_keywords.append(keyword)

        if added_keywords:
            await sync_to_async(profile.save)()

        response = ""
        if added_keywords:
            response += await get_text(message.from_user.id, 'keyword_added', text=", ".join(added_keywords)) + "\n"
        if existing_keywords:
            response += await get_text(message.from_user.id, 'keyword_exists') + f": {', '.join(existing_keywords)}"

        await message.answer(response or await get_text(message.from_user.id, 'keyword_exists'))
        await state.clear()
        await message.delete()

    except TelegramProfile.DoesNotExist:
        await message.answer(await get_text(message.from_user.id, 'not_linked'))
        await state.clear()
        await message.delete()


# --- Удаление фильтра ---
@dp.message(Command("delfilter"))
@dp.message(F.text.contains("🗑️"))
async def del_filter(message: types.Message, state: FSMContext):
    await message.answer(await get_text(message.from_user.id, 'enter_del_keyword'))
    await state.set_state(Form.waiting_for_del_filter)
    await message.delete()


@dp.message(Form.waiting_for_del_filter)
async def handle_del_filter(message: types.Message, state: FSMContext):
    text = message.text.strip()
    try:
        profile = await sync_to_async(TelegramProfile.objects.get)(telegram_id=message.from_user.id)

        # Обрабатываем несколько слов через запятую
        keywords = [kw.strip() for kw in text.split(',') if kw.strip()]
        deleted_keywords = []
        not_found_keywords = []

        for keyword in keywords:
            if keyword in profile.filters:
                profile.filters.remove(keyword)
                deleted_keywords.append(keyword)
            else:
                not_found_keywords.append(keyword)

        if deleted_keywords:
            await sync_to_async(profile.save)()

        response = ""
        if deleted_keywords:
            response += await get_text(message.from_user.id, 'keyword_deleted', text=", ".join(deleted_keywords)) + "\n"
        if not_found_keywords:
            response += await get_text(message.from_user.id, 'keyword_not_found') + f": {', '.join(not_found_keywords)}"

        await message.answer(response or await get_text(message.from_user.id, 'keyword_not_found'))
        await state.clear()
        await message.delete()

    except TelegramProfile.DoesNotExist:
        await message.answer(await get_text(message.from_user.id, 'not_linked'))
        await state.clear()
        await message.delete()


# --- Список фильтров ---
@dp.message(Command("listfilters"))
@dp.message(F.text.contains("📋"))
async def list_filters(message: types.Message):
    await message.delete()
    try:
        profile = await sync_to_async(TelegramProfile.objects.get)(telegram_id=message.from_user.id)
        if profile.filters:
            await message.answer(
                await get_text(message.from_user.id, 'filters_list') + ", ".join(profile.filters)
            )
        else:
            await message.answer(await get_text(message.from_user.id, 'no_filters'))
    except TelegramProfile.DoesNotExist:
        await message.answer(await get_text(message.from_user.id, 'not_linked'))


# --- Обработка неизвестных команд ---
@dp.message()
async def unknown_command(message: types.Message):
    await message.answer(
        f"{await get_text(message.from_user.id, 'unknown_command')}\n"
        "/start, /addfilter, /delfilter, /listfilters, /help, /lang",
        reply_markup=await get_main_keyboard(message.from_user.id)
    )


@dp.inline_query()
async def inline_vacancy_search(inline_query: InlineQuery):
    query = inline_query.query.strip().lower()
    user_id = inline_query.from_user.id

    if not query:
        title = await get_text(user_id, 'inline_search_title')
        description = await get_text(user_id, 'inline_search_description')
        message = await get_text(user_id, 'inline_search_message')

        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text="Другие вакансии",
                    web_app=WebAppInfo(url="https://quality-herring-fine.ngrok-free.app"),  # твой URL
                )]
            ]
        )

        results = [InlineQueryResultArticle(
            id="1", title=title, description=description,
            input_message_content=InputTextMessageContent(message_text=message),
        )]
    else:
        vacancies = await sync_to_async(
            lambda: list(
                Vacancy.objects.filter(
                    title__icontains=query,
                    is_active=True
                ).order_by('-published_at')[:20]
            )
        )()

        if not vacancies:
            title = await get_text(user_id, 'inline_no_results_title')
            description = await get_text(user_id, 'inline_no_results_description', query=query)
            message = await get_text(user_id, 'inline_no_results_message', query=query)

            results = [InlineQueryResultArticle(
                id="no_results", title=title, description=description,
                input_message_content=InputTextMessageContent(message_text=message)
            )]
        else:
            results = []
            for i, vacancy in enumerate(vacancies):
                # Локализованное описание
                salary_text = await get_text(user_id, 'salary')
                location_text = await get_text(user_id, 'location')

                description = f"{vacancy.salary} {salary_text} • {vacancy.city or location_text}"
                if vacancy.work_type:
                    description += f" • {vacancy.get_work_type_display()}"

                view_text = await get_text(user_id, 'view_vacancy')


                results.append(InlineQueryResultArticle(
                    id=str(vacancy.id),
                    title=vacancy.title,
                    description=description,
                    input_message_content=InputTextMessageContent(
                        message_text=await format_vacancy_message(user_id, vacancy, query),
                        parse_mode="HTML"
                    ),
                ))

    await inline_query.answer(results, cache_time=60, is_personal=True)


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