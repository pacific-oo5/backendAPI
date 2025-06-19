from django.apps import AppConfig
from django.conf import settings
from django.core.management import call_command
import threading
import os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            return

        def run_all():
            try:
                print("Загрузка стран и городов...")
                call_command('cities_light')
                print("Применение русских названий...")
                call_command('update_ru_names', './cities/alternateNamesV2.txt')
                print("Загрузка завершена.")
            except Exception as e:
                print(f"Ошибка при автозагрузке: {e}")

        threading.Thread(target=run_all).start()
