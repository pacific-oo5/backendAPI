# api/permissions.py
from rest_framework import permissions

class HasUserRPermission(permissions.BasePermission):
    """
    Разрешение для пользователей, у которых user_r = True.
    """
    message = 'У вас нет разрешения на выполнение этого действия.' # Сообщение об ошибке, если нет доступа

    def has_permission(self, request, view):
        # Разрешаем GET, HEAD, OPTIONS запросы для всех (чтение данных)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для POST (создание) и других небезопасных методов:
        # Проверяем, авторизован ли пользователь и имеет ли он user_r = True
        return request.user and request.user.is_authenticated and request.user.user_r