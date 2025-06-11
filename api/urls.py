from django.urls import path
from api.views import (
    VacancyListView,
    VacancyCreateView,
    VacancyDetailView,
    VacancyUpdateView,
    VacancyDeleteView
)

urlpatterns = [
    path('vacancies/', VacancyListView.as_view(), name='vacancy-list'),
    path('vacancies/create/', VacancyCreateView.as_view(), name='vacancy-create'),
    path('vacancies/<int:pk>/', VacancyDetailView.as_view(), name='vacancy-detail'),
    path('vacancies/<int:pk>/update/', VacancyUpdateView.as_view(), name='vacancy-update'),
    path('vacancies/<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancy-delete'),
]