from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

from userauth.models import CustomUser
from .choices import STATUS_CHOICES, WORK_CHOICES, WORK_TIME_CHOICES, ACTION_CHOICES
from django.utils.translation import gettext_lazy as _


class Vacancy(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='vacancies',
        verbose_name=_('Владелец вакансии'),
        help_text=_('Пользователь, разместивший вакансию')
    )
    title = models.CharField(
        verbose_name=_('Название'),
        max_length=100,
        help_text=_('Название вакансии, например: Python разработчик')
    )
    description = models.TextField(
        verbose_name=_('Описание'),
        help_text=_('Краткое описание вакансии')
    )
    about_me = models.TextField(
        verbose_name=_('О вас или компании'),
        help_text=_('Информация о работодателе или команде')
    )
    work_type = models.CharField(
        verbose_name=_('Тип занятости'),
        choices=WORK_CHOICES,
        max_length=20,
        help_text=_('Выберите тип занятости: полная или частичная')
    )
    work_time = models.CharField(
        choices=WORK_TIME_CHOICES,
        max_length=20,
        help_text=_('Выберите время работы: день или ночь')
    )
    salary = models.IntegerField(
        verbose_name=_('Зарплата'),
        help_text=_('Укажите зарплату в сомах'),
        blank=True,
        null=True
    )
    country = models.CharField(
        null=True,
        verbose_name=_('Страна'),
        help_text=_('Страна, где предлагается вакансия')
    )
    city = models.CharField(
        null=True,
        verbose_name=_('Город'),
        help_text=_('Город, где предлагается вакансия')
    )
    is_remote = models.BooleanField(
        verbose_name=_('Удаленный'),
        default=False,
        help_text=_('Отметьте, если работа удалённая')
    )
    requirements = models.TextField(
        verbose_name=_('Требования'),
        help_text=_('Требуемые навыки и квалификация')
    )
    responsibilities = models.TextField(
        verbose_name=_('Обязанности'),
        help_text=_('Что нужно будет делать на работе')
    )
    published_at = models.DateTimeField(
        auto_now=True,
        help_text=_('Дата последней публикации вакансии')
    )
    is_active = models.BooleanField(
        verbose_name=_('Активен'),
        default=True,
        help_text=_('Если выключить, вакансия будет скрыта')
    )

    favorite_by = models.ManyToManyField(
        CustomUser, related_name='favorite_vacancies', blank=True
    )

    def get_absolute_url(self):
        return reverse('api:vacancy_detail', kwargs={'pk': self.pk})

    def get_responded_workers(self):
        return [resp.worker.id for resp in self.responses.all()] # type: ignore

    def __str__(self):
        return str(self.title)


class VacancyView(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    user = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    ip = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(null=True, blank=True)
    referrer = models.URLField(null=True, blank=True)
    country = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)

    action = models.CharField(max_length=20, choices=ACTION_CHOICES, default="view")

    viewed_at = models.DateTimeField(auto_now_add=True)
    
    
class VacancyResponse(models.Model):
    worker = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Откликнувшийся воркер')
    )
    vacancy = models.ForeignKey(
        'Vacancy',
        on_delete=models.CASCADE,
        related_name='responses',
        verbose_name=_('Вакансия')
    )
    is_favorite = models.BooleanField(default=False, verbose_name=_('Избранное'))
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Статус отклика')
    )
    anketa = models.ForeignKey(
        'Anketa',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='responses',
        verbose_name=_('Анкета')
    )

    responded_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    @property
    def status_choices(self):
        return STATUS_CHOICES

    
    class Meta:
        unique_together = ('worker', 'vacancy')


class Anketa(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ankets',
        help_text=_('Пользователь, к которому привязана анкета')
    )
    title = models.CharField(
        verbose_name=_('Название'),
        help_text=_('Название анкеты, например: Backend разработчик')
    )
    about_me = models.TextField(
        verbose_name=_('Обо мне'),
        help_text=_('Расскажите кратко о себе, навыках и целях')
    )
    experience = models.TextField(
        verbose_name=_('Опыт работы'),
        help_text=_('Опишите, где и кем вы работали ранее')
    )
    country = models.CharField(
        null=True,
        verbose_name=_('Страна'),
        help_text=_('Укажите страну проживания')
    )
    city = models.CharField(
        null=True,
        verbose_name=_('Город'),
        help_text=_('Укажите город проживания')
    )
    phone_number = models.CharField(
        max_length=20,
        verbose_name=_('Телефон'),
        help_text=_('Введите номер телефона в формате +996XXXXXXXXX')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Активна ли анкета'),
        help_text=_('Если выключить, анкета будет скрыта из поиска')
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Дата создания анкеты')
    )

    def __str__(self):
        return f"{self.title} ({self.user.email})"


class VacancyComplaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='vacancy_complaints'
    )
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='complaints')
    reason = models.TextField()  # причина жалобы
    anon_name = models.CharField(max_length=100, blank=True, null=True)  # имя анонима
    anon_email = models.EmailField(blank=True, null=True)  # email анонима
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Жалоба на вакансию")
        verbose_name_plural = _("Жалобы на вакансии")
        ordering = ['-created_at']

    def __str__(self):
        if self.user:
            return f"{self.user} пожаловался на {self.vacancy}"
        return str(_("Аноним пожаловался на ")) + str(self.vacancy)