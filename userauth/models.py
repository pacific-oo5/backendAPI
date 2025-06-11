from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        """
        Создает и сохраняет пользователя с заданным email и паролем.
        """
        if not email:
            raise ValueError('Поле Email должно быть установлено.')
        email = self.normalize_email(email) # Приводит email к нормализованному виду (например, нижний регистр домена)
        user = self.model(email=email, **extra_fields) # Создаем экземпляр пользователя с email
        user.set_password(password) # Устанавливаем пароль
        user.save(using=self._db) # Сохраняем в базу данных
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True) # Убедитесь, что суперпользователь активен по умолчанию

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперпользователь должен иметь is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперпользователь должен иметь is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=False,
        null=True,
        blank=True,
        verbose_name='Имя пользователя (не используется для входа)'
    )

    # Переопределяем поле 'email' из AbstractUser
    email = models.EmailField(
        unique=True,
        blank=False,
        null=False,
        verbose_name='Электронная почта'
    )

    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')

    user_r = models.BooleanField(
        verbose_name="Разрешение на публикацию вакансий",
        default=True,
    )

    # Определяем, какое поле будет использоваться для аутентификации
    USERNAME_FIELD = 'email'

    # Поля, которые будут запрашиваться при создании суперпользователя (кроме USERNAME_FIELD и пароля)
    REQUIRED_FIELDS = ['username']

    # <-- САМОЕ ВАЖНОЕ: Назначьте ваш собственный менеджер для модели!
    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        # Опциональные метаданные для админки
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        # Указываем Django, что эта модель должна использоваться вместо встроенной User
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        # Красивое строковое представление пользователя
        return self.email  # Отображаем email пользователя