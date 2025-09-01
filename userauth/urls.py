from django.urls import path
from .views import ProfileView, PublicProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView
)

app_name='userauth'
urlpatterns = [
    path('profile/', ProfileView.as_view(), name='profile'),
    path('user/<int:pk>/', PublicProfileView.as_view(), name='public_profile'),
]

urlpatterns += [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # получение access и refresh
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # обновление access по refresh
]