from django.urls import path
from . import views

app_name="miniapp"
urlpatterns = [
    path("", views.MiniAppVacancyPageView.as_view(), name='main'),
    path('filter/', views.MiniAppFilterView.as_view(), name='filter'),
    path("profile/", views.ProfilePageView.as_view(), name="profile"),
    path("profile/data/", views.MiniAppProfileDataView.as_view(), name="profile_data"),
]