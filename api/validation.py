import re
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError

def validate_phone_number(value):
    pattern = re.compile(r'^\+?\d{10,15}$')
    if not pattern.match(value):
        raise ValidationError(
            _('Неверный формат номера телефона. Укажите в формате +996XXXXXXXXX или без +.'),
            params={'value': value},
        )


def validate_telegram(value):
    pattern = re.compile(r'^[a-zA-Z0-9_]{5,32}$')
    if not pattern.match(value):
        raise ValidationError('Неверное имя Telegram. Укажите без @, только имя пользователя.')