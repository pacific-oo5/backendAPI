from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.utils.translation import gettext_lazy as _


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'user_r', 'is_staff')
    list_filter = ('user_r', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', )}),
        (_('Персональная информация'), {'fields': ('first_name', 'user_r')}),
        (_('Права'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Важные даты'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_r'),
        }),
    )
    search_fields = ('email', 'first_name')
    ordering = ('email',)
