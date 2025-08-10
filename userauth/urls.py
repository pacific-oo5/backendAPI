from dj_rest_auth.views import LoginView, LogoutView, PasswordResetView, PasswordChangeView
from django.urls import path
from .views import CustomRegisterView, ProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    # path('csrf/', get_csrf_token, name='get_csrf_token'),
    # path("user/", UserDetailsView.as_view(), name="user-details"),
    # path('register/', CustomRegisterView.as_view(), name='rest_register'),
    # path('login/', LoginView.as_view(), name='rest_login'),
    # path('logout/', LogoutView.as_view(), name='rest_logout'),
]

urlpatterns += [
    # path('password-reset/', PasswordResetView.as_view(), name='rest_password_reset'),
    # path('password-change/', PasswordChangeView.as_view(), name='rest_password_change'),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # получение access и refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление access по refresh
]