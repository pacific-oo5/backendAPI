from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

admin.site.register(CustomUser, UserAdmin)

# Если вы хотите добавить или изменить отображение полей в админке для CustomUser,
# вы можете создать свой собственный Admin-класс:
# class CustomUserAdmin(UserAdmin):
#     # Добавьте ваше поле 'user_r' в список отображаемых полей
#     fieldsets = UserAdmin.fieldsets + (
#         ('Дополнительные поля', {'fields': ('user_r',)}),
#     )
#     # Или добавьте его в list_display для таблицы
#     list_display = UserAdmin.list_display + ('user_r',)

# admin.site.register(CustomUser, CustomUserAdmin)