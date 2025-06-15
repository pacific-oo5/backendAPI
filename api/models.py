from django.db import models
from django.contrib.auth import get_user_model

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
        related_name='vacancies',  # Обратное отношение для удобства
        verbose_name='Владелец вакансии'
    )
    name = models.CharField(verbose_name='Название', max_length=100)
    description = models.TextField(verbose_name='Описание')
    about_me = models.TextField(verbose_name='О вас или компании')
    work_type = models.CharField(verbose_name='Тип занятости', choices=WORK_CHOICES, max_length=20)
    work_time = models.CharField(choices=WOKR_TIME_CHOICES, max_length=20)
    salary = models.IntegerField(verbose_name='Зарплата')
    location = models.CharField(verbose_name='Локация', max_length=255)
    is_remote = models.BooleanField(verbose_name='Удаленный', default=False)
    requirements = models.TextField(verbose_name='Требования')
    responsibilities = models.TextField(verbose_name='Обязанности')
    published_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(verbose_name='Активен', default=True)


    def get_responded_workers(self):
        return [resp.worker.id for resp in self.responses.all()]

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
        verbose_name='Статус отклика',
    )

    class Meta:
        unique_together = ('worker', 'vacancy')  # Один отклик на одну вакансию
