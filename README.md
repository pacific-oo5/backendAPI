# Django App

Простая инструкция по установке и запуску Django-приложения.

## ⚙️ Требования

- Python 3.10+
- Git

## 🚀 Установка

```bash
# 1. Клонировать репозиторий
git clone https://github.com/pacific-oo5/backendAPI.git
cd backendAPI

# 2. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # для Linux/macOS
venv\Scripts\activate     # для Windows

# 3. Установить зависимости
pip install -r requirements.txt

# 4. Создать .env файл (если нужен) и настроить переменные окружения
# Пример:
# DEBUG=True
# SECRET_KEY=your-secret-key
# DATABASE_URL=...

# 5. Выполнить миграции
python manage.py makemigrations
python manage.py migrate

# 6. Создать суперпользователя (по желанию)
python manage.py createsuperuser

# 7. Запустить сервер
python manage.py runserver
