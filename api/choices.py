from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = (
    ('pending', _('Ожидание')),
    ('accepted', _('Принят')),
    ('rejected', _('Отклонён')),
)

WORK_CHOICES = (
    ('work', _('Работа')),
    ('practice', _('Практика')),
)

WORK_TIME_CHOICES = (
    ('flexible', _('Гибкий график')),
    ('full_time', _('Полный рабочий день')),
    ('weekends', _('По выходным'))
)

ACTION_CHOICES = [
        ("view", _("Просмотр")),
        ("response", _("Отклик")),
    ]