from django.urls import path
from .views import AnketaCreateView, VacancyCreateView, VacancyListView, vacancy_delete, vacancy_toggle, \
    VacancyUpdateView, VacancyDetailView, vacancy_stats, respond_to_vacancy, \
    AnketaDetailView, AnketaUpdateView, response_update_status, vacancy_complaint, toggle_favorite

app_name = 'api'
urlpatterns = [
    path('vacancies', VacancyListView.as_view(), name='vacancy_list'),
    path('vacancies/<int:pk>/', VacancyDetailView.as_view(), name='vacancy_detail'),
    path('vacancy/create', VacancyCreateView.as_view(), name='vacancy_create'),
    path('vacancy/<int:pk>/toggle/', vacancy_toggle, name='vacancy_toggle'),
    path('vacancy/<int:pk>/delete/', vacancy_delete, name='vacancy_delete'),
    path("vacancy/<int:pk>/stats/", vacancy_stats, name="vacancy_stats"),
    path('vacancy/<int:pk>/update/', VacancyUpdateView.as_view(), name='vacancy_update'),
    path('vacancies/<int:pk>/respond/', respond_to_vacancy, name='respond_to_vacancy'),
    path('response/<int:pk>/update-status/', response_update_status, name='response_update_status'),
    path('vacancy/<int:vacancy_id>/complaint/', vacancy_complaint, name='vacancy_complaint'),
    path("vacancy/<int:vacancy_id>/favorite/", toggle_favorite, name="toggle_favorite"),
]

urlpatterns += [
    path('anketa/create/', AnketaCreateView.as_view(), name='anketa_create'),
    path('anketa/<int:pk>/', AnketaDetailView.as_view(), name='anketa_detail'),
    path('anketa/<int:pk>/edit/', AnketaUpdateView.as_view(), name='anketa_edit'),
]