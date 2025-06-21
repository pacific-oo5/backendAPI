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