from django.urls import path
from .views import PunchInOutView, UserAttendanceStatsView , AllAttendanceStatsView

urlpatterns = [
    path('punch/', PunchInOutView.as_view(), name='punch-in-out'),
    path('stats/', UserAttendanceStatsView.as_view(), name='attendance-stats'),
    path ('get-all/',AllAttendanceStatsView.as_view(), name='get-allattendance-stats' )
]
