import asyncio
from aiogram import Bot
from aiogram.client.bot import DefaultBotProperties
from telegram_bot.utils import get_text
from userauth.models import TelegramProfile
from api.models import Vacancy, VacancyResponse
from asgiref.sync import sync_to_async
import os
from dotenv import load_dotenv
import logging

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logger = logging.getLogger(__name__)
_bot_instance = None


def get_bot():
    """Singleton Bot instance"""
    global _bot_instance
    if _bot_instance is None:
        _bot_instance = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    return _bot_instance


# --- Уведомление подписчикам о новой вакансии ---
async def notify_users(vacancy: Vacancy, user_id):
    bot = get_bot()
    try:
        # Получаем профили синхронно
        profiles_qs = TelegramProfile.objects.exclude(telegram_id=None)
        profiles = await sync_to_async(list)(profiles_qs)

        sent_count = 0

        for profile in profiles:
            if not profile.filters:
                continue

            if any(keyword.lower() in vacancy.title.lower() for keyword in profile.filters):
                try:
                    await asyncio.sleep(0.1)
                    salary_text = await get_text(user_id, 'salary')
                    location_text = await get_text(user_id, 'location')
                    view_text = await get_text(user_id, 'view_vacancy_button')
                    vacancy_url = f"https://quality-herring-fine.ngrok-free.app/vacancies/{vacancy.id}/"
                    await bot.send_message(
                        chat_id=profile.telegram_id,
                        text=f"Новая вакансия: <b>{vacancy.title}</b>\n\n"
                             f"Описание: {vacancy.description[:200]}...\n\n"
                             f"Зарплата: {vacancy.salary} сом\n"
                             f"Город: {vacancy.city}\n"
                             f"Тип работы: {vacancy.get_work_type_display()}\n\n"
                             f"<a href='{vacancy_url}'>{view_text}</a>"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Ошибка отправки пользователю {profile.telegram_id}: {e}")

        logger.info(f"Всего уведомлений отправлено: {sent_count}")
    except Exception as e:
        logger.error(f"Ошибка в notify_users: {e}")
    finally:
        await bot.session.close()


async def notify_vacancy_author(telegram_id, response):
    bot = get_bot()
    try:
        text = (
            f"{await get_text(telegram_id, 'new_response', title=response.vacancy.title)}\n\n"
            f"{await get_text(telegram_id, 'candidate', username=response.worker.username,
                              experience=response.anketa.experience,
                              city=response.anketa.city or 'Remote')}"
        )

        await bot.send_message(chat_id=telegram_id, text=text)
        logger.info(f"Уведомление автору вакансии {telegram_id} отправлено")

    except Exception as e:
        logger.error(f"Ошибка notify_vacancy_author: {e}")

    finally:
        await bot.session.close()


async def notify_status_change(telegram_id, response):
    bot = get_bot()
    try:
        employer_profile = await sync_to_async(lambda: getattr(response.vacancy.user, "telegram_profile", None))()

        status_text = "✅ Принят" if response.status == "accepted" else "❌ Отклонён"
        if employer_profile and employer_profile.username:
            employer_contact = f"@{employer_profile.username}"
        else:
            employer_contact = "Работодатель не указал Telegram"

        text = (
            f"Ваш отклик на вакансию «{response.vacancy.title}» был обновлён.\n\n"
            f"Контакт работодателя: {employer_contact}\n\n"
            f"Статус: {status_text}"
        )

        await bot.send_message(chat_id=telegram_id, text=text)
        logger.info(f"Уведомление воркеру {telegram_id} отправлено")

    except Exception as e:
        logger.error(f"Ошибка notify_status_change: {e}", exc_info=True)
    finally:
        await bot.session.close()
