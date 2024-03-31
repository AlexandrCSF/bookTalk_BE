from django.urls import path
from clubs.views import ClubCardView

urlpatterns = [
    path('club/', ClubCardView.as_view(), name='get_club'),
]
