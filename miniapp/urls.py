from django.urls import path
from . import views

app_name="miniapp"
urlpatterns = [
    path("", views.MiniAppVacancyPageView.as_view(), name='main'),
    path('filter/', views.MiniAppFilterView.as_view(), name='filter'),
    path("profile/", views.profile, name="profile"),
    path("profile/data/", views.profile_data, name="profile_data"),
]