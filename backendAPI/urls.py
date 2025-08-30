from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from userauth.views import AuthView, CustomLoginView, CustomRegisterView, CustomLogoutView, ProfileView, \
    select_role_view, PublicProfileView
from api.views import VacancyListView
from .views import *

urlpatterns = [
path('i18n/', include('django.conf.urls.i18n')),
    path('', VacancyListView.as_view(), name='home'),
    path('', include('api.urls'), name='api'),
    path('privacy/', privacy_policy, name='privacy_policy'),
    path('terms/', terms_of_service, name='terms_of_service'),
    path('miniapp/', include('miniapp.urls'), name='miniapp'),
    path('admin/', admin.site.urls),
    path('employers/', employers, name='employers'),
    path('applicants/', applicants, name='applicants'),
]

urlpatterns += [
    path('', include('userauth.urls'), name='userauth'),
]

urlpatterns += [
    path('auth/', AuthView.as_view(), name='auth'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', CustomRegisterView.as_view(), name='register'),
    path('select-role/', select_role_view, name='select_role'),
    path('accounts/', include('allauth.urls')),
    path('logout/', CustomLogoutView.as_view(), name='custom_logout'),
    path('auth/social/', include('allauth.socialaccount.urls')),
]

urlpatterns += [
    path('rosetta/', include('rosetta.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)