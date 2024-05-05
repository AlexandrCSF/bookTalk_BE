from django.urls import path
from clubs.views import ClubCardView, ClubUsersView, MemberView, AdminView, SubscribeView

urlpatterns = [
    path('club/', ClubCardView.as_view(), name='get_club'),
    path('users/', ClubUsersView.as_view()),
    path('membership_for_user/', MemberView.as_view()),
    path('administrated_clubs_for_user', AdminView.as_view()),
    path('subscribe/', SubscribeView.as_view()),
]
