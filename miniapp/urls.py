from django.urls import path
from . import views

app_name="miniapp"
urlpatterns = [
    path("", views.MiniAppVacancyPageView.as_view(), name='main'),
    path("profile/", views.ProfilePageView.as_view(), name="profile"),
    path("settings/", views.SettingsPageView.as_view(), name="settings"),
    path("anketas/", views.user_anketas, name="miniapp_user_anketas"),
    path("profile/data/", views.MiniAppProfileDataView.as_view(), name="profile_data"),
    path('profile/data/2/', views.profile_data, name='profile_data2'),
    path("profile/responses/", views.MiniAppProfileResponsesView.as_view(), name="miniapp_profile_responses"),
]

urlpatterns += [
    path('vacancies/by_keywords/', views.vacancies_by_keywords, name='vacancies_by_keywords'),
    path('vacancies/<int:pk>/edit/', views.vacancy_edit, name='vacancy_edit'),
    path('vacancies/<int:pk>/delete/', views.vacancy_delete, name='vacancy_delete'),
    path('vacancies/<int:pk>/', views.MiniAppVacancyDetailView.as_view(), name='vacancy_detail'),
    path("vacancies/<int:pk>/respond/", views.miniapp_respond_vacancy, name="respond_vacancy"),
    path("vacancies/<int:pk>/favorite/", views.miniapp_toggle_favorite, name="toggle_favorite"),
    path("vacancies/has_responded/", views.MiniAppVacancyDetailView.as_view(), name="has_responded"),
    path('vacancies/<int:pk>/has_responded/', views.has_responded, name='has_responded'),

    path('favorites/', views.FavoriteVacanciesView.as_view(), name='favorite_vacancies'),
    path('favorites/data/', views.MiniAppFavoriteVacanciesDataView.as_view(), name='favorite_vacancies_data'),
]

urlpatterns += [
    path('filter/', views.MiniAppFilterView.as_view(), name='filter'),
    path('filters/', views.get_filters, name='get_filters'),
    path('filters/get/', views.get_filters, name='get_filters'),
    # Добавление/удаление ключевых слов
    path('filters/update/', views.update_filters, name='update_filters'),
]