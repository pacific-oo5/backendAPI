from django.urls import path
from .views import ProfileView, PublicProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
]

urlpatterns += [
    # path('password-reset/', PasswordResetView.as_view(), title='rest_password_reset'),
    # path('password-change/', PasswordChangeView.as_view(), title='rest_password_change'),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # получение access и refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление access по refresh
]