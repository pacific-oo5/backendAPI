import uuid
from allauth.socialaccount.models import SocialAccount
from .models import TelegramProfile


def get_google_avatar(user):
    try:
        account = SocialAccount.objects.get(user=user, provider='google')
        return account.extra_data.get('picture')  # URL аватара
    except SocialAccount.DoesNotExist:
        return None

def generate_unique_token():
    while True:
        token = uuid.uuid4().hex
        if not TelegramProfile.objects.filter(token=token).exists():
            return token