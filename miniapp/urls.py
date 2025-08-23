from django.urls import path
from . import views

app_name="miniapp"
urlpatterns = [
    path("", views.MiniAppVacancyPageView.as_view(), name='miniapp_main'),
    path('filter/', views.MiniAppFilterView.as_view(), name='miniapp_filter'),
]