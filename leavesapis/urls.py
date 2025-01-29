from django.urls import path
from .views import ApplyLeaveView , ApproveRejectLeaveView , UserLeaveRecordsView , GetAllLeavesView

urlpatterns = [
    path('apply/', ApplyLeaveView.as_view(), name='apply-leave'),
    path('update-status/', ApproveRejectLeaveView.as_view(), name='approve-leave'),
    path('<int:user_id>/', UserLeaveRecordsView.as_view(), name='user-leaves'),
    path('get-all/', GetAllLeavesView.as_view(), name='list-leaves'),



]
