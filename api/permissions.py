from rest_framework.permissions import BasePermission


class IsRecruiter(BasePermission):
    """Для пользователей с user_r=True (могут создавать вакансии)"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_r


class IsNotRecruiter(BasePermission):
    def has_permission(self, request, view):
        return not request.user.user_r