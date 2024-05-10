from django.urls import path

from authorisation.views import UserView, FreeTokenView, RefreshTokenView

urlpatterns = [
    path('token/free', FreeTokenView.as_view(), name='token_free'),
    path('token/refresh/', RefreshTokenView.as_view(), name='token_refresh'),
    path('user/',UserView.as_view())
]
