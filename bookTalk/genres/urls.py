from django.urls import path
from genres.views import GenresView

urlpatterns = [
    path('', GenresView.as_view(), name='genres')
]
