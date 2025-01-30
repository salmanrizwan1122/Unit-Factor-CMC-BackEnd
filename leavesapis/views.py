from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, activate
from datetime import datetime
from datetime import timedelta, date 
from rest_framework.exceptions import NotFound
from ufcmsdb.models import Leave, CustomUser  # Adjust the import to match your project structure

class ApplyLeaveView(APIView):
    """
    View for applying for a leave.
    """
    def post(self, request):
        activate('Asia/Karachi')
        user_id = request.data.get('user_id')  # Get user ID from request data
        leave_type = request.data.get('leave_type')
        leave_from = request.data.get('leave_from')
        leave_to = request.data.get('leave_to')
        reason = request.data.get('reason')
        
        if not user_id or not leave_type or not leave_from or not leave_to or not reason:
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)  # Retrieve the user object
        except User.DoesNotExist:
            return Response({"message": "Invalid User ID."}, status=status.HTTP_400_BAD_REQUEST)

        leave_from_date = datetime.strptime(leave_from, '%Y-%m-%d').date()
        leave_to_date = datetime.strptime(leave_to, '%Y-%m-%d').date()
        leave_days = (leave_to_date - leave_from_date).days + 1

        # Check leave balances
        if leave_days > user.monthly_leave_balance:
            return Response({"message": "Not enough monthly leave balance."}, status=status.HTTP_400_BAD_REQUEST)
        
        if leave_days > user.yearly_leave_balance:
            return Response({"message": "Not enough yearly leave balance."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create leave record
        leave = Leave(
            user=user,
            leave_type=leave_type,
            leave_from=leave_from_date,
            leave_to=leave_to_date,
            reason=reason,
            status='Pending',  # Set initial status to Pending
            leave_days=leave_days
        )
        leave.save()

        # Deduct leave days from balances
        return Response({
            "message": "Leave applied successfully.",
            "leave_id": leave.id,
            "leave_days": leave_days,
            "monthly_leave_balance": user.monthly_leave_balance,
            "yearly_leave_balance": user.yearly_leave_balance
        }, status=status.HTTP_201_CREATED)
class ApproveRejectLeaveView(APIView):
    """
    View for approving or rejecting leave requests.
    """
    def post(self, request):
        activate('Asia/Karachi')
        leave_id = request.data.get('leave_id')  # Get leave ID from request data
        action = request.data.get('action')  # Get action (approve or reject)
        approved_by_id = request.data.get('approved_by')  # Get approver's user ID
        
        if not leave_id or not action or not approved_by_id:
            return Response({"message": "Leave ID, action, and approver's user ID are required."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            leave = Leave.objects.get(id=leave_id)  # Retrieve the leave object
        except Leave.DoesNotExist:
            return Response({"message": "Invalid Leave ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            approver = User.objects.get(id=approved_by_id)  # Retrieve the approver user object
        except User.DoesNotExist:
            return Response({"message": "Invalid Approver User ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure action is either 'approve' or 'reject'
        if action not in ['approve', 'reject']:
            return Response({"message": "Action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        # Update leave status and balances based on action
        if action == 'approve':
            leave.status = 'Approved'
            leave.approved_by = approver.user_name  # Store approver's username
            leave.approved_date = date.today()
            leave.approved_time = datetime.now().time()
            
            # Deduct leave days from balances if not already deducted
            if leave.leave_days <= leave.user.monthly_leave_balance:
                leave.user.monthly_leave_balance -= leave.leave_days
            else:
                return Response({"message": "Not enough monthly leave balance."}, status=status.HTTP_400_BAD_REQUEST)
            
            if leave.leave_days <= leave.user.yearly_leave_balance:
                leave.user.yearly_leave_balance -= leave.leave_days
            else:
                return Response({"message": "Not enough yearly leave balance."}, status=status.HTTP_400_BAD_REQUEST)

            leave.user.save()
        else:
            leave.status = 'Rejected'
            leave.approved_by = approver.user_name  # Store approver's username
            leave.approved_date = date.today()
            leave.approved_time = datetime.now().time()

        leave.save()

        return Response({
            "message": f"Leave {leave.status.lower()} successfully.",
            "leave_id": leave.id,
            "status": leave.status,
            "approved_by": leave.approved_by,
            "approved_date": leave.approved_date,
            "approved_time": leave.approved_time,
            
        }, status=status.HTTP_200_OK)
class GetAllLeavesView(APIView):
    """
    View to get all leave records.
    """
    def get(self, request):
        leaves = Leave.objects.all().values(
            'id', 'user__user_name',  'user_id', 'leave_type', 'leave_from', 'leave_to', 'status', 'reason',
            'approved_by', 'approved_date', 'approved_time', 'leave_days'
        )
        return Response({"leaves": list(leaves)}, status=status.HTTP_200_OK)
class UserLeaveRecordsView(APIView):
    """
    View to get leave records by user ID.
    """
    def get(self, request, user_id):
        # Validate user existence
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound({"message": "User not found."})

        leaves = Leave.objects.filter(user=user).values(
            'id', 'leave_type', 'leave_from', 'leave_to', 'status', 'reason',
            'approved_by', 'approved_date', 'approved_time', 'leave_days'
        )
        return Response({"user": user.user_name, "leaves": list(leaves)}, status=status.HTTP_200_OK)

