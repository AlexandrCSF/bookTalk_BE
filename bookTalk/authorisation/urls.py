from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from authorisation.views import UserView, FreeTokenView

urlpatterns = [
    path('token/free', FreeTokenView.as_view(), name='token_free'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/',UserView.as_view())
]
