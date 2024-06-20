from django.urls import path

from meetings.views import MeetingView, AttendanceView, WontAttendView

urlpatterns = [
    path('meeting/', MeetingView.as_view()),
    path('attend/', AttendanceView.as_view()),
    path('wont_attend/', WontAttendView.as_view())
]
