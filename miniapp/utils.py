import hashlib
import hmac
import urllib.parse
import os

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
