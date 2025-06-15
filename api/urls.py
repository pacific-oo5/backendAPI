from django.urls import path
from .views import RespondToVacancyView, AddToFavoritesView, RespondedUsersView, MyVacancyListView, \
    AcceptOrRejectResponseView, UserResponsesView, FavoriteVacancyListView
from api.views import (
    VacancyListView,
    VacancyCreateView,
    VacancyDetailView,
    VacancyUpdateView,
    VacancyDeleteView,
)

urlpatterns = [
    path('vacancies/', VacancyListView.as_view(), name='vacancy-list'),
    path('vacancies/my/', MyVacancyListView.as_view(), name='my-vacancy-list'),
    path('my-responses/', UserResponsesView.as_view(), name='my-responses'),
    path('vacancies/favorites/', FavoriteVacancyListView.as_view(), name='favorite-vacancies'),

    path('vacancies/create/', VacancyCreateView.as_view(), name='vacancy-create'),
    path('vacancies/<int:pk>/', VacancyDetailView.as_view(), name='vacancy-detail'),
    path('vacancies/<int:pk>/update/', VacancyUpdateView.as_view(), name='vacancy-update'),
    path('vacancies/<int:pk>/delete/', VacancyDeleteView.as_view(), name='vacancy-delete'),
    path('vacancies/<int:pk>/respond/', RespondToVacancyView.as_view(), name='vacancy-respond'),
    path('vacancies/<int:vacancy_id>/responses/', RespondedUsersView.as_view(), name='vacancy-responses'),
path('vacancies/<int:vacancy_id>/responses/<int:worker_id>/set_status/', AcceptOrRejectResponseView.as_view(), name='set-response-status'),
    path('vacancies/<int:pk>/favorite/', AddToFavoritesView.as_view(), name='vacancy-favorite'),
]