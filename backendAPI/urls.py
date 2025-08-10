from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.views.decorators.cache import never_cache

from userauth.views import AuthView, CustomLoginView, CustomRegisterView, CustomLogoutView, ProfileView, select_role_view
from api.views import VacancyListView, VacancyDetailView
from .views import *

index_view = never_cache(TemplateView.as_view(template_name='index.html'))


urlpatterns = [
    path('', VacancyListView.as_view(), name='home'),
    path('', include('api.urls'), name='api'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('admin/', admin.site.urls),
    path('employers/', employers, name='employers'),
    path('applicants/', applicants, name='applicants'), 
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

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)