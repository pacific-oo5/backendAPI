from django.urls import path
from .views import RespondToVacancyView, AddToFavoritesView, RespondedUsersView, \
    VacancyDetailView, AcceptOrRejectResponseView, UserResponsesView, \
    FavoriteVacancyListView, MyContentView, AnketaViewSet, PublicAnketaViewSet, VacancyResponsesView
from rest_framework.routers import DefaultRouter
from api.views import VacancyListView, VacancyViewSet

anketa_public = PublicAnketaViewSet.as_view({'get': 'retrieve'})

router = DefaultRouter()
router.register(r'my/vacancies', VacancyViewSet, basename='my-vacancies')
router.register(r'my/anketas', AnketaViewSet, basename='anketa')


urlpatterns = [
    path('vacancies/', VacancyListView.as_view(), name='vacancy-list'),
    path('vacancies/<int:pk>/', VacancyDetailView.as_view(), name='vacancy-detail'),
    path('anketas/@<str:username>/anketa/<int:pk>/', anketa_public, name='public-anketa-detail'),
    path('vacancies/favorites/', FavoriteVacancyListView.as_view(), name='favorite-vacancies'),
    path('vacancies/<int:pk>/respond/', RespondToVacancyView.as_view(), name='vacancy-respond'),
    path('vacancies/<int:vacancy_id>/responses/', RespondedUsersView.as_view(), name='vacancy-responses'),
    path('vacancies/<int:pk>/favorite/', AddToFavoritesView.as_view(), name='vacancy-favorite'),
]

urlpatterns += [
    path('my/', MyContentView.as_view(), name='my'),
    path('my/responses/', UserResponsesView.as_view(), name='my-responses'),
]

urlpatterns += [
    path('vacancies/<int:vacancy_id>/responses/<int:response_id>/set_status/', AcceptOrRejectResponseView.as_view(), name='set-response-status'),
    path('vacancies/<int:vacancy_id>/responses/', VacancyResponsesView.as_view(), name='vacancy-responses'),
    path('vacancies/favorites/', FavoriteVacancyListView.as_view(), name='favorite-vacancies'),
]

urlpatterns += router.urls