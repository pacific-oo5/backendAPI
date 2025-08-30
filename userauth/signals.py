from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import CustomUser, TelegramProfile, EmployerProfile, JobSeekerProfile


@receiver(post_save, sender=CustomUser)
def create_telegram_profile(sender, instance, created, **kwargs):
    if created:
        TelegramProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_r:
            EmployerProfile.objects.create(user=instance, displayname=instance.username)
        else:
            JobSeekerProfile.objects.create(user=instance, displayname=instance.username)