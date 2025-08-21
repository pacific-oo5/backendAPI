from django.contrib import admin
from django.utils.html import format_html
from .models import Vacancy, VacancyResponse, Anketa

class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'work_type', 'salary', 'country_city', 'is_active', 'published_at')
    list_filter = ('work_type', 'work_time', 'is_active', 'is_remote', 'published_at')
    search_fields = ('title', 'description', 'user__email')
    readonly_fields = ('published_at',)
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'about_me', 'salary')
        }),
        ('Детали вакансии', {
            'fields': ('work_type', 'work_time', 'country', 'city', 'is_remote')
        }),
        ('Требования', {
            'fields': ('requirements', 'responsibilities'),
            'classes': ('collapse',)
        }),
        ('Статус', {
            'fields': ('is_active', 'published_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Работодатель'
    
    def country_city(self, obj):
        return f"{obj.country}, {obj.city}" if obj.country and obj.city else "-"
    country_city.short_description = 'Локация'

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление

class VacancyResponseAdmin(admin.ModelAdmin):
    list_display = ('vacancy_name', 'worker_email', 'status_badge', 'is_favorite', 'responded_at')
    list_filter = ('status', 'is_favorite', 'responded_at')
    search_fields = ('vacancy__name', 'worker__email')
    readonly_fields = ('responded_at',)
    
    def vacancy_name(self, obj):
        return obj.vacancy.title
    vacancy_name.short_description = 'Вакансия'
    
    def worker_email(self, obj):
        return obj.worker.email
    worker_email.short_description = 'Соискатель'
    
    def status_badge(self, obj):
        colors = {
            'pending': 'orange',
            'accepted': 'green',
            'rejected': 'red'
        }
        return format_html(
            '<span style="color: white; background-color: {}; padding: 3px 8px; border-radius: 10px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Статус'
    status_badge.admin_order_field = 'status'

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление


class AnketaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'country_city', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'about_me', 'user__email')
    readonly_fields = ('created_at', 'user_profile_link')
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'user_profile_link', 'title', 'about_me')
        }),
        ('Опыт работы', {
            'fields': ('experience',),
            'classes': ('collapse',)
        }),
        ('Контактные данные', {
            'fields': ('country', 'city', 'phone_number')
        }),
        ('Статус', {
            'fields': ('is_active', 'created_at')
        }),
    )
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Пользователь'
    
    def country_city(self, obj):
        return f"{obj.country}, {obj.city}" if obj.country and obj.city else "-"
    country_city.short_description = 'Локация'
    
    def user_profile_link(self, obj):
        url = f"/admin/userauth/customuser/{obj.user.id}/change/"
        return format_html('<a href="{}">Профиль пользователя</a>', url)
    user_profile_link.short_description = 'Профиль'

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление


# Регистрация моделей
admin.site.register(Vacancy, VacancyAdmin)
admin.site.register(VacancyResponse, VacancyResponseAdmin)
admin.site.register(Anketa, AnketaAdmin)