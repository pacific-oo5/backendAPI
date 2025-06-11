from django.db import models
from multiselectfield import MultiSelectField
from django.contrib.auth import get_user_model


class Vacancy(models.Model):
    EMPLOYMENT_TYPE_CHOICES = {
        'ПЗ': 'Полная занятость',
        'НПЗ': 'Не полная занятность',
        'СТ': 'Стажировка'
    }
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='vacancies',  # Обратное отношение для удобства
        verbose_name='Владелец вакансии'
    )
    name = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField(verbose_name='Описание')
    about_me = models.TextField(verbose_name='О вас или компании')
    employment_type = MultiSelectField(
        verbose_name='Тип занятости',
        choices=EMPLOYMENT_TYPE_CHOICES,
        max_choices=3,
        max_length=10
    )
    salary_min = models.IntegerField(verbose_name='Минимальный зарплата')
    salary_max = models.IntegerField(verbose_name='Максимальный зарплата')
    location = models.CharField(verbose_name='Локация', max_length=255)
    is_remote = models.BooleanField(verbose_name='Удаленный', default=False)
    requirements = models.TextField(verbose_name='Требования')
    responsibilities = models.TextField(verbose_name='Обязанности')
    published_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)



