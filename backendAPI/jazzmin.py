from django.utils.translation import gettext_lazy as _

JAZZMIN_SETTINGS = {
    # Основные настройки брендинга
    "site_title": _("СЛАДКИЙ МАЛЬЧИК"),
    "site_header": _("СЛАДКИЙ МАЛЬЧИК"),
    "site_brand": _("СЛАДКИЙ МАЛЬЧИК"),

    # Полностью убираем логотип
    "site_logo": 'main/logo/logo.png',
    "site_logo_classes": None,
    "site_icon": 'main/logo/logo.png',

    "navigation_expanded": True,
    "hide_navbar": True,
    # Тексты
    "welcome_sign": _("Добро пожаловать в административную панель"),
    "copyright": _("СЛАДКИЙ МАЛЬЧИК"),

    # Поиск - упрощаем для мобильных
    "search_model": [],

    ############
    # Top Menu #
    ############
    "topmenu_links": [
        {"model": "auth.User"},
        {"model": "userauth.CustomUser"},
        {"app": "api"},
    ],

    #############
    # User Menu #
    #############
    "usermenu_links": [
        {"model": "auth.user"},
    ],

    #############
    # Side Menu #
    #############
    "show_sidebar": True,
    "hide_apps": [
        "authtoken",      # Auth Token
        "sites",          # Sites
        "socialaccount",  # Social Accounts (для allauth)
        "social_django",

    ],
    "hide_models": [
        'auth.group'
    ],
    "order_with_respect_to": ["auth", "api"],

    # Кастомные ссылки
    "custom_links": {
        "api": [{
            "title": "Вакансии",
            "url": "admin:api_vacancy_changelist",
            "icon": "fas fa-briefcase",
        }],
        "userauth": [{
            "title": "Пользователи",
            "url": "admin:userauth_customuser_changelist",
            "icon": "fas fa-users",
        }]
    },

    # Иконки для приложений и моделей
    "icons": {
        # Auth app
        "auth": "fas fa-users-cog",
        "auth.user": "fas fa-user",
        "auth.Group": "fas fa-users",

        # API app
        "api": "fas fa-code",
        "api.Vacancy": "fas fa-briefcase",
        "api.VacancyResponse": "fas fa-file-alt",
        "api.Anketa": "fas fa-clipboard-list",

        # Userauth app
        "userauth": "fas fa-user-shield",
        "userauth.CustomUser": "fas fa-user-tie",
    },

    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",

    #################
    # Related Modal #
    #################
    "related_modal_active": True,

    #############
    # UI Tweaks #
    #############
    "custom_css": "jazzmin/css/custom_admin.css",
    "custom_js": "jazzmin/js/admin_custom.js",  # Добавляем кастомный JS
    "use_google_fonts_cdn": True,

    ###############
    # Change view #
    ###############
    "changeform_format": "collapsible",  # Более мобильно-дружественный формат
    "changeform_format_overrides": {
        "auth.user": "collapsible",
        "userauth.customuser": "collapsible",
        "api.vacancy": "collapsible",
        "api.vacancyresponse": "collapsible"
    },
    "language_chooser": True,  # Отключаем для мобильных
    # Полностью убираем футер
    "show_footer": False,

    # Дополнительные настройки
    "show_ui_builder": True,
    "show_version": None,
}

JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": False,
    "footer_small_text": False,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": False,
    "accent": None,
    "navbar": "navbar-light navbar-white",
    "no_navbar_border": True,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark",
    "sidebar_nav_small_text": False,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": False,
    "sidebar_nav_compact_style": False,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "journal",
    "dark_mode_theme": "cyborg",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    },
    "sidebar_brand": None,
    "actions_sticky_top": True
}