from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, TelegramProfile

@receiver(post_save, sender=CustomUser)
def create_telegram_profile(sender, instance, created, **kwargs):
    if created:
        TelegramProfile.objects.create(user=instance)
