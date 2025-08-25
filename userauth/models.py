import secrets
import uuid

from django.conf import settings
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Поле Email должно быть установлено.'))
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
            raise ValueError(_('Суперпользователь должен иметь is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Суперпользователь должен иметь is_superuser=True.'))

        return self._create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=False,
        null=True,
        blank=True,
        verbose_name=_('Имя пользователя')
    )

    email = models.EmailField(unique=True, blank=False, null=False, verbose_name=_('Электронная почта'))
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_('Имя'))
    user_r = models.BooleanField(verbose_name=_("Разрешение на публикацию вакансий"), default=False)
    telegram_id = models.BigIntegerField(unique=True, null=True, blank=True, verbose_name="Telegram ID")
    telegram_token = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    class Meta(AbstractUser.Meta):
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')
        swappable = 'AUTH_USER_MODEL'

    def __str__(self):
        return self.email
    
    # @property
    # def avatar(self):
    #     if self.photo:
    #         return self.photo.url
    #     return f'{settings.STATIC_URL}images/avatar.svg'


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    displayname = models.CharField(max_length=20, null=True, blank=True)
    info = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.user)

    @property
    def name(self):
        if self.displayname:
            return self.displayname
        return self.user.username

def generate_unique_token():
    while True:
        token = uuid.uuid4().hex
        if not TelegramProfile.objects.filter(token=token).exists():
            return token


class ProfileToken(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_token",
    )
    value = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rotated_at = models.DateTimeField(null=True, blank=True)


    @staticmethod
    def generate() -> str:
        # 32 байта → 64 hex-символа
        return secrets.token_hex(32)


    @classmethod
    def ensure_for_user(cls, user):
        obj, created = cls.objects.get_or_create(
        user=user,
        defaults={"value": cls.generate()},
        )
        return obj


class TelegramProfile(models.Model):
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='telegram_profiles'
    )
    telegram_id = models.BigIntegerField(blank=True, null=True)
    avatar_url = models.CharField(blank=True, null=True)
    token = models.CharField(max_length=32, unique=True, default=generate_unique_token)
    username = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=64, null=True, blank=True)
    last_name = models.CharField(max_length=64, null=True, blank=True)
    is_connected = models.BooleanField(default=False)
    filters = models.JSONField(default=list) # список ключевых слов
    language = models.CharField(max_length=10, default='ru', choices=[
        ('kg', 'Кыргызча'),
        ('ru', 'Русский'),
        ('en', 'English')
    ])

    def generate_new_token(self):
        import uuid

        self.token = uuid.uuid4().hex
        self.save()

    def __str__(self):
        return f"tg:{self.telegram_id} → user:{self.user_id}"