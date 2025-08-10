from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def save_user(self, request, sociallogin, form=None):
        """
        Сохраняет пользователя с дополнительным полем user_r
        при регистрации через социальные сети
        """
        user = super().save_user(request, sociallogin, form)
        
        # Получаем user_r из запроса или данных формы
        user_r = request.POST.get('user_r', False) or request.data.get('user_r', False)
        user.user_r = bool(user_r)
        user.save()
        
        return user

    def get_user_search_fields(self, sociallogin):
        """
        Обязательный метод для поиска пользователя.
        Используем email как основной идентификатор.
        """
        return ['email']

    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Разрешаем автоматическую регистрацию через соцсети
        """
        return True

    def pre_social_login(self, request, sociallogin):
        """
        Дополнительная обработка перед входом через соцсети
        """
        # Можно добавить дополнительную логику здесь
        super().pre_social_login(request, sociallogin)