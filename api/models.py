from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model

from api.validation import validate_phone_number


STATUS_CHOICES = (
        ('pending', 'Ожидание'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонён'),
    )
WORK_CHOICES = (
        ('Работа', 'Работа'),
        ('Практика', 'Практика'),
    )
WOKR_TIME_CHOICES = (
    ('Гибкий график', 'Гибкий график'),
    ('Полный рабочий день', 'Полный рабочий день'),
    ('По выходным', 'По выходным')
)


class Vacancy(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='vacancies',
        verbose_name='Владелец вакансии',
        help_text='Пользователь, разместивший вакансию'
    )
    name = models.CharField(
        verbose_name='Название',
        max_length=100,
        help_text='Название вакансии, например: Python разработчик'
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Краткое описание вакансии'
    )
    about_me = models.TextField(
        verbose_name='О вас или компании',
        help_text='Информация о работодателе или команде'
    )
    work_type = models.CharField(
        verbose_name='Тип занятости',
        choices=WORK_CHOICES,
        max_length=20,
        help_text='Выберите тип занятости: полная или частичная'
    )
    work_time = models.CharField(
        choices=WOKR_TIME_CHOICES,
        max_length=20,
        help_text='Выберите время работы: день или ночь'
    )
    salary = models.IntegerField(
        verbose_name='Зарплата',
        help_text='Укажите зарплату в сомах'
    )
    country = models.CharField(
        null=True,
        verbose_name='Страна',
        help_text='Страна, где предлагается вакансия'
    )
    city = models.CharField(
        null=True,
        verbose_name='Город',
        help_text='Город, где предлагается вакансия'
    )
    is_remote = models.BooleanField(
        verbose_name='Удаленный',
        default=False,
        help_text='Отметьте, если работа удалённая'
    )
    requirements = models.TextField(
        verbose_name='Требования',
        help_text='Требуемые навыки и квалификация'
    )
    responsibilities = models.TextField(
        verbose_name='Обязанности',
        help_text='Что нужно будет делать на работе'
    )
    published_at = models.DateTimeField(
        auto_now=True,
        help_text='Дата последней публикации вакансии'
    )
    is_active = models.BooleanField(
        verbose_name='Активен',
        default=True,
        help_text='Если выключить, вакансия будет скрыта'
    )


    def get_responded_workers(self):
        return [resp.worker.id for resp in self.responses.all()]

    def telegram_link(self):
        if self.telegram:
            return f"https://t.me/{self.telegram}"
        return None

    def __str__(self):
        return str(self.name)


class VacancyResponse(models.Model):
    worker = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Откликнувшийся воркер'
    )
    vacancy = models.ForeignKey(
        'Vacancy',
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name='Вакансия'
    )
    is_favorite = models.BooleanField(default=False, verbose_name='Избранное')
    responded_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Статус отклика'
    )
    anketa = models.ForeignKey(
        'Anketa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responses',
        verbose_name='Анкета'
    )

    class Meta:
        unique_together = ('worker', 'vacancy')


class Anketa(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ankets',
        help_text='Пользователь, к которому привязана анкета'
    )
    name = models.CharField(
        verbose_name='Название',
        help_text='Название анкеты, например: Backend разработчик'
    )
    about_me = models.TextField(
        verbose_name='Обо мне',
        help_text='Расскажите кратко о себе, навыках и целях'
    )
    experience = models.TextField(
        verbose_name='Опыт работы',
        help_text='Опишите, где и кем вы работали ранее'
    )
    country = models.CharField(
        null=True,
        verbose_name='Страна',
        help_text='Укажите страну проживания'
    )
    city = models.CharField(
        null=True,
        verbose_name='Город',
        help_text='Укажите город проживания'
    )
    phone_number = models.CharField(
        max_length=20,
        validators=[validate_phone_number],
        verbose_name='Телефон',
        help_text='Введите номер телефона в формате +996XXXXXXXXX'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна ли анкета',
        help_text='Если выключить, анкета будет скрыта из поиска'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='Дата создания анкеты'
    )

    def __str__(self):
        return f"{self.name} ({self.user.email})"
