from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import re

phone_validator = RegexValidator(
    regex=r'^\+([1-9][0-9]{0,2})[0-9]{7,12}$',
    message="Номер телефона должен быть в формате +<код страны><номер>"
)

def validate_positive(value):
    if value is not None and value < 0:
        raise ValidationError("Значение должно быть положительным")

# Проверка минимальной длины текста
def validate_min_length(value, min_length=10):
    if value and len(value.strip()) < min_length:
        raise ValidationError(f"Поле должно содержать не менее {min_length} символов")

# Проверка, что текст содержит только буквы, пробелы и базовые символы
def validate_text_only(value):
    if value and not re.match(r'^[\w\s.,-]+$', value, re.UNICODE):
        raise ValidationError("Поле содержит недопустимые символы")