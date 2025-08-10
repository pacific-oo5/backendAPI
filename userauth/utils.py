from allauth.socialaccount.models import SocialAccount

def get_google_avatar(user):
    try:
        account = SocialAccount.objects.get(user=user, provider='google')
        return account.extra_data.get('picture')  # URL аватара
    except SocialAccount.DoesNotExist:
        return None
