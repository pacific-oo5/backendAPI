from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Редактировать может только владелец"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class IsVacancyOwnerOrReadOnly(permissions.BasePermission):
    """Отклики может просматривать только автор вакансии"""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return obj.vacancy.user == request.user
        return obj.worker == request.user or obj.vacancy.user == request.user
