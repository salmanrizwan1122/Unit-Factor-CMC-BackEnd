from django.urls import path
from .views import PunchInOutView, AttendanceStatsView

urlpatterns = [
    path('punch/', PunchInOutView.as_view(), name='punch-in-out'),
    path('stats/', AttendanceStatsView.as_view(), name='attendance-stats'),
]
