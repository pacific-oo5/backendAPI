import logging
from django.db.models.signals import post_save
from django.dispatch import receiver

from userauth.models import TelegramProfile
from .models import Vacancy, VacancyResponse
from telegram_bot.telegram_utils import notify_users, notify_vacancy_author
import asyncio
import threading

logger = logging.getLogger(__name__)


def run_async_in_thread(coroutine):
    def run():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(coroutine)
        finally:
            loop.close()
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


@receiver(post_save, sender=Vacancy)
def vacancy_created(sender, instance, created, **kwargs):
    if created:
        logger.info(f"Вакансия создана: {instance.title}, запускаю уведомления...")
        user_id = instance.user.id
        run_async_in_thread(notify_users(instance, user_id))
        # Запускаем асинхронную задачу в отдельном потоке
        logger.info("Задача уведомлений запущена в отдельном потоке")


@receiver(post_save, sender=VacancyResponse)
def vacancy_response_created(sender, instance, created, **kwargs):
    if created:
        profile = TelegramProfile.objects.filter(user=instance.vacancy.user).first()
        if profile and profile.telegram_id:
            run_async_in_thread(notify_vacancy_author(profile.telegram_id, instance))
        else:
            logger.info(f"Автор вакансии {instance.vacancy.user.id} не подключил Telegram")
