from django.urls import path
from clubs.views import ClubCardView, ClubUsersView, MemberView

urlpatterns = [
    path('club/', ClubCardView.as_view(), name='get_club'),
    path('users/', ClubUsersView.as_view()),
    path('membership/', MemberView.as_view())
]
