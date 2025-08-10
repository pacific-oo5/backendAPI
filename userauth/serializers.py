from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer as DefaultUserDetailsSerializer
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from .models import CustomUser


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'photo', 'user_r']

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    
    def save_user(self, request, sociallogin, form=None):
        """Сохраняет пользователя с дополнительным полем user_r"""
        user = super().save_user(request, sociallogin, form)
        
        # Получаем user_r из запроса или устанавливаем False по умолчанию
        user_r = request.data.get('user_r', False)
        user.user_r = user_r
        user.save()
        
        return user

    def get_user_search_fields(self, sociallogin):
        """Обязательный метод для поиска пользователя"""
        default_fields = super().get_user_search_fields(sociallogin)
        # Добавляем email как основное поле для поиска
        return default_fields + ['email']

    def is_auto_signup_allowed(self, request, sociallogin):
        """Разрешаем автоматическую регистрацию"""
        return True

    def pre_social_login(self, request, sociallogin):
        """Дополнительная обработка перед входом"""
        super().pre_social_login(request, sociallogin)
        
        
        