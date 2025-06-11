from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.urls import path
from .views import CustomRegisterView


urlpatterns = [
    path('register/', CustomRegisterView.as_view(), name='rest_register'),
    path('login/', LoginView.as_view(), name='rest_login'), # URL для входа (добавьте слеш!)
    path('logout/', LogoutView.as_view(), name='rest_logout'), # URL для выхода
    path('password-reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    path('password-change/', PasswordChangeView.as_view(), name='rest_password_change'),
]