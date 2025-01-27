from django.urls import path
from .views import ApplyLeaveView

urlpatterns = [
    path('apply/', ApplyLeaveView.as_view(), name='apply-leave'),
]
