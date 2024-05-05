from django.urls import path

from meetings.views import MeetingView,AttendanceView

urlpatterns = [
    path('meeting/', MeetingView.as_view()),
    path('attend/', AttendanceView.as_view()),
]
