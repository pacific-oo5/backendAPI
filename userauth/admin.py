from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, TelegramProfile


class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'user_r', 'is_staff')
    list_filter = ('user_r', 'is_staff', 'is_superuser')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональная информация', {'fields': ('first_name', 'user_r')}),
        ('Права', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'user_r'),
        }),
    )
    search_fields = ('email', 'first_name')
    ordering = ('email',)

@admin.register(TelegramProfile)
class TelegramProfileAdmin(admin.ModelAdmin):
    list_display = ['username']

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление

    def has_view_permission(self, request, obj=None):
        return True

admin.site.register(CustomUser, CustomUserAdmin)

