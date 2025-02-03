from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now, activate
from datetime import datetime
from datetime import timedelta, date 
from rest_framework.exceptions import NotFound
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from ufcmsdb.models import Leave, CustomUser  # Adjust the import to match your project structure

class ApplyLeaveView(APIView):
    """
    View for applying for a leave.
    """
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        activate('Asia/Karachi')
        user = request.user  # Get the authenticated user from the token

        # Check if the user has permission to apply for leave
        has_permission = user.role.filter(permissions__action="create", permissions__module="leave").exists()
        if not has_permission:
            return Response({"message": "You do not have permission to apply for leave."}, status=status.HTTP_403_FORBIDDEN)

        # Extract data from the request
        leave_type = request.data.get('leave_type')
        leave_from = request.data.get('leave_from')
        leave_to = request.data.get('leave_to')
        reason = request.data.get('reason')

        # Validate required fields
        if not leave_type or not leave_from or not leave_to or not reason:
            return Response({"message": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Parse dates
        try:
            leave_from_date = datetime.strptime(leave_from, '%Y-%m-%d').date()
            leave_to_date = datetime.strptime(leave_to, '%Y-%m-%d').date()
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate leave days
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
        user.monthly_leave_balance -= leave_days
        user.yearly_leave_balance -= leave_days
        user.save()

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
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def post(self, request):
        activate('Asia/Karachi')
        user = request.user  # Get the authenticated user from the token

        # Check if the user has permission to approve/reject leave
        has_permission = user.role.filter(permissions__action="update", permissions__module="leave").exists()
        if not has_permission:
            return Response({"message": "You do not have permission to approve or reject leave requests."}, status=status.HTTP_403_FORBIDDEN)

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
            approver = CustomUser.objects.get(id=approved_by_id)  # Retrieve the approver user object
        except CustomUser.DoesNotExist:
            return Response({"message": "Invalid Approver User ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure action is either 'approve' or 'reject'
        if action not in ['approve', 'reject']:
            return Response({"message": "Action must be 'approve' or 'reject'."}, status=status.HTTP_400_BAD_REQUEST)

        # Update leave status and balances based on action
        if action == 'approve':
            leave.status = 'Approved'
            leave.approved_by = approver.username  # Store approver's username
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
            leave.approved_by = approver.username  # Store approver's username
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
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request):
        user = request.user  # Get the authenticated user from the token

        # Check if the user has permission to view all leaves
        has_permission = user.role.filter(permissions__action="view", permissions__module="leave").exists()
        if not has_permission:
            return Response({"message": "You do not have permission to view all leave records."}, status=status.HTTP_403_FORBIDDEN)

        leaves = Leave.objects.all().values(
            'id', 'user__user_name',  'user_id', 'leave_type', 'leave_from', 'leave_to', 'status', 'reason',
            'approved_by', 'approved_date', 'approved_time', 'leave_days'
        )
        return Response({"leaves": list(leaves)}, status=status.HTTP_200_OK)

class UserLeaveRecordsView(APIView):
    """
    View to get leave records by user ID.
    """
    authentication_classes = [TokenAuthentication]  # Use token authentication
    permission_classes = [IsAuthenticated]  # Ensure the user is authenticated

    def get(self, request, user_id):
        user = request.user  # Get the authenticated user from the token

        # Check if the user has permission to view leave records
        has_permission = user.role.filter(permissions__action="view", permissions__module="leave").exists()
        if not has_permission:
            return Response({"message": "You do not have permission to view leave records."}, status=status.HTTP_403_FORBIDDEN)

        # Validate user existence
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            raise NotFound({"message": "User not found."})

        # Ensure the user is viewing their own records or has permission to view others' records
        if user.id != target_user.id and not user.role.filter(permissions__action="view_all", permissions__module="leave").exists():
            return Response({"message": "You do not have permission to view this user's leave records."}, status=status.HTTP_403_FORBIDDEN)

        leaves = Leave.objects.filter(user=target_user).values(
            'id', 'leave_type', 'leave_from', 'leave_to', 'status', 'reason',
            'approved_by', 'approved_date', 'approved_time', 'leave_days'
        )

        return Response({"user": target_user.user_name, "leaves": list(leaves)}, status=status.HTTP_200_OK)