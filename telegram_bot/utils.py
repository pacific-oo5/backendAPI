from telegram_bot.localization import get_user_language, TEXTS


async def get_text(telegram_id, text_key, **kwargs):
    """Получаем текст на языке пользователя асинхронно"""
    lang = await get_user_language(telegram_id)
    text = TEXTS[lang].get(text_key, text_key)
    return text.format(**kwargs) if kwargs else text