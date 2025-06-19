from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from .validation import validate_profile_username

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Поле Email должно быть установлено.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

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
    email = models.EmailField(unique=True, blank=False, null=False, verbose_name='Электронная почта')
    first_name = models.CharField(max_length=150, blank=True, verbose_name='Имя')
    user_r = models.BooleanField(verbose_name="Разрешение на публикацию вакансий", default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email