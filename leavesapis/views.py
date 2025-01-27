from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import date
from ufcmsdb.models import Leave, User  # Adjust the import to match your project structure


class ApplyLeaveView(APIView):
    """
    API View to apply for a new leave.
    """
    def post(self, request):
        user_id = request.data.get('user_id')  # Get user ID from the request data
        leave_type = request.data.get('leave_type')
        leave_from = request.data.get('leave_from')
        leave_to = request.data.get('leave_to')
        reason = request.data.get('reason')

        # Validate required fields
        if not all([user_id, leave_type, leave_from, leave_to, reason]):
            return Response(
                {"message": "All fields (user_id, leave_type, leave_from, leave_to, reason) are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validate user
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({"message": "Invalid user ID."}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate leave days
        try:
            leave_from_date = date.fromisoformat(leave_from)
            leave_to_date = date.fromisoformat(leave_to)
            if leave_to_date < leave_from_date:
                return Response({"message": "Leave 'to' date cannot be earlier than 'from' date."}, status=status.HTTP_400_BAD_REQUEST)
            leave_days = (leave_to_date - leave_from_date).days + 1
        except ValueError:
            return Response({"message": "Invalid date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Check leave balance (assuming `leave_balance` is tracked on the user or elsewhere)
        leave_balance = user.profile.leave_balance  # Adjust if leave balance is stored differently
        if leave_days > leave_balance:
            return Response(
                {"message": "Insufficient leave balance.", "available_leave_balance": leave_balance},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create leave request
        leave = Leave.objects.create(
            user=user,
            leave_type=leave_type,
            leave_from=leave_from_date,
            leave_to=leave_to_date,
            leave_date=date.today(),
            reason=reason,
            leave_days=leave_days,
            leave_balance=leave_balance - leave_days,
        )

        return Response(
            {"message": "Leave applied successfully.", "leave_id": leave.id, "leave_status": leave.status},
            status=status.HTTP_201_CREATED,
        )
