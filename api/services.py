from django.db import transaction
from django.contrib.auth import get_user_model
from userauth.models import ProfileToken, TelegramProfile




class TokenAttachResult:
    def __init__(self, user, telegram_profile, reattached: bool):
        self.user = user
        self.telegram_profile = telegram_profile
        self.reattached = reattached




@transaction.atomic
def attach_token_to_telegram(telegram_id: int, token_value: str, **kwargs) -> TokenAttachResult:
    """
    Находит пользователя по токену и привязывает/обновляет TelegramProfile(telegram_id → user).
    Если telegram_id уже был привязан к другому user — перекидываем на нового (по секретному токену это ок).
    """
    try:
        token = ProfileToken.objects.select_for_update().select_related("user").get(value=token_value)
    except ProfileToken.DoesNotExist:
        raise ValueError("INVALID_TOKEN")


    tg, created = TelegramProfile.objects.select_for_update().get_or_create(
        telegram_id=telegram_id,
        defaults={
            "user": token.user,
            **{k: v for k, v in kwargs.items() if k in {"username", "first_name", "last_name"}},
        },
    )


    reattached = False
    if tg.user_id != token.user_id:
        tg.user = token.user
        for k in ("username", "first_name", "last_name"):
            if k in kwargs:
                setattr(tg, k, kwargs[k])
        tg.save()
        reattached = True


    return TokenAttachResult(user=token.user, telegram_profile=tg, reattached=reattached)