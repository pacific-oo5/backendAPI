from rest_framework.permissions import BasePermission
from django.conf import settings

class IsRecruiter(BasePermission):
    """Для пользователей с user_r=True (могут создавать вакансии)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_r


class IsNotRecruiter(BasePermission):
    def has_permission(self, request, view):
        return not request.user.user_r


class IsFromBot(BasePermission):
    """Запросы только от бота через X-Api-Key."""
    def has_permission(self, request, view):
        api_key = request.headers.get("X-Api-Key")
        return bool(api_key and api_key == getattr(settings, "BOT_API_KEY", None))