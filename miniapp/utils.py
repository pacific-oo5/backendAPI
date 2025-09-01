import hashlib
import hmac
import json
import urllib.parse
import os
from urllib.parse import parse_qs

BOT_TOKEN = os.getenv("BOT_TOKEN")

def check_telegram_auth(init_data: str) -> bool:
    parsed = dict(urllib.parse.parse_qsl(init_data))
    hash_from_telegram = parsed.pop("hash", None)

    # формируем data_check_string
    data_check_arr = [f"{k}={v}" for k, v in sorted(parsed.items())]
    data_check_string = "\n".join(data_check_arr)

    # секретный ключ
    secret_key = hmac.new(
        key=b"WebAppData",
        msg=BOT_TOKEN.encode(),
        digestmod=hashlib.sha256
    ).digest()

    # считаем хеш
    calculated_hash = hmac.new(
        secret_key, data_check_string.encode(), hashlib.sha256
    ).hexdigest()

    return calculated_hash == hash_from_telegram


def get_tg_id(request):
    """
    Извлекает Telegram ID из initData заголовка или GET-параметра
    """
    # Пробуем получить из заголовка
    init_data = request.headers.get('X-Telegram-Init-Data')

    # Если нет в заголовке, пробуем из GET-параметра
    if not init_data:
        init_data = request.GET.get('initData')

    # Если нет вообще, возвращаем None
    if not init_data:
        return None

    try:
        # Парсим initData
        parsed_data = parse_qs(init_data)
        user_data = parsed_data.get('user', ['{}'])[0]
        user_json = json.loads(user_data)
        return str(user_json.get('id'))  # Преобразуем в строку для надежности
    except (json.JSONDecodeError, KeyError, IndexError, TypeError):
        return None


def get_tg_user_data(request):
    """
    Получает все данные пользователя из initData
    """
    init_data = request.headers.get('X-Telegram-Init-Data') or request.GET.get('initData')
    if not init_data:
        return None

    try:
        parsed_data = parse_qs(init_data)
        user_data = parsed_data.get('user', ['{}'])[0]
        return json.loads(user_data)
    except (json.JSONDecodeError, KeyError, IndexError):
        return None