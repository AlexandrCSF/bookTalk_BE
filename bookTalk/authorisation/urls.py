from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('token/free', TokenObtainPairView.as_view(), name='token_free'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh')
]
