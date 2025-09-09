import logging
from asgiref.sync import async_to_sync
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from userauth.models import TelegramProfile
from .models import Vacancy, VacancyResponse
from telegram_bot.telegram_utils import notify_users, notify_vacancy_author, notify_status_change
import asyncio
import threading

logger = logging.getLogger(__name__)


def run_async_in_thread(coro):
    def run():
        try:
            asyncio.run(coro)
        except Exception as e:
            logger.error(f"Ошибка в run_async_in_thread: {e}")
    threading.Thread(target=run, daemon=True).start()


@receiver(post_save, sender=Vacancy)
def vacancy_created(sender, instance, created, **kwargs):
    if created:
        run_async_in_thread(notify_users(instance, instance.user.id))
        logger.info("Уведомления о новой вакансии запущены")


# Уведомляем работодателя о новом отклике
@receiver(post_save, sender=VacancyResponse)
def vacancy_response_created(sender, instance, created, **kwargs):
    if created:
        employer_profile = TelegramProfile.objects.filter(user=instance.vacancy.user).first()
        if employer_profile and employer_profile.telegram_id:
            run_async_in_thread(notify_vacancy_author(employer_profile.telegram_id, instance))
            logger.info(f"Уведомление работодателю {employer_profile.telegram_id} отправлено")
        else:
            logger.warning(f"Нет Telegram профиля у работодателя {instance.vacancy.user}")
