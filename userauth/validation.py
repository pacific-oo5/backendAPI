import re
from django.core.exceptions import ValidationError

def validate_profile_username(value):
    pattern = re.compile(r'^[a-zA-Z0-9_]{3,32}$')
    if not pattern.match(value):
        raise ValidationError('Неверное имя профиля. Разрешены только буквы, цифры и _ (3-32 символа).')