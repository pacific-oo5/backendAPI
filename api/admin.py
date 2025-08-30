from django.contrib import admin
from django.utils.html import format_html
from .models import Vacancy, VacancyResponse, Anketa, VacancyComplaint
from django.utils.translation import gettext_lazy as _

@admin.register(Vacancy)
class VacancyAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'work_type', 'salary', 'country_city', 'is_active', 'published_at')
    list_filter = ('work_type', 'work_time', 'is_active', 'is_remote', 'published_at')
    search_fields = ('title', 'description', 'user__email')
    readonly_fields = ('published_at',)
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'title', 'description', 'about_me', 'salary')
        }),
        (_('Детали вакансии'), {
            'fields': ('work_type', 'work_time', 'country', 'city', 'is_remote')
        }),
        (_('Требования'), {
            'fields': ('requirements', 'responsibilities'),
            'classes': ('collapse',)
        }),
        (_('Статус'), {
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


@admin.register(VacancyResponse)
class VacancyResponseAdmin(admin.ModelAdmin):
    list_display = ('vacancy_name', 'worker_email', 'status_badge', 'is_favorite', 'responded_at')
    list_filter = ('status', 'is_favorite', 'responded_at')
    search_fields = ('vacancy__title',)
    readonly_fields = ('responded_at',)
    
    def vacancy_name(self, obj):
        return obj.vacancy.title
    vacancy_name.short_description = _('Вакансия')
    
    def worker_email(self, obj):
        return obj.worker.email
    worker_email.short_description = _('Соискатель')
    
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
    status_badge.short_description = _('Статус')
    status_badge.admin_order_field = 'status'

    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление


@admin.register(Anketa)
class AnketaAdmin(admin.ModelAdmin):
    list_display = ('title', 'user_email', 'country_city', 'phone_number', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'about_me', 'user__email')
    readonly_fields = ('created_at', 'user_profile_link')
    fieldsets = (
        (_('Основная информация'), {
            'fields': ('user', 'title', 'about_me')
        }),
        (_('Опыт работы'), {
            'fields': ('experience',),
            'classes': ('collapse',)
        }),
        (_('Контактные данные'), {
            'fields': ('country', 'city', 'phone_number')
        }),
        (_('Статус'), {
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


@admin.register(VacancyComplaint)
class VacancyComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'vacancy', 'user_display', 'anon_name', 'created_at', 'short_reason')
    list_filter = ('created_at', 'vacancy')
    search_fields = ('vacancy__title', 'user__username', 'anon_name', 'anon_email', 'reason')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
    list_select_related = ('vacancy', 'user')

    def user_display(self, obj):
        return obj.user.username if obj.user else "Аноним"
    user_display.short_description = "Пользователь"

    def short_reason(self, obj):
        return obj.reason[:50] + ("..." if len(obj.reason) > 50 else "")
    short_reason.short_description = "Причина"


    def has_add_permission(self, request):
        return False  # запрет на добавление

    def has_change_permission(self, request, obj=None):
        return False  # запрет на редактирование

    def has_delete_permission(self, request, obj=None):
        return True  # разрешить только удаление