from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from ufcmsdb.models import Attendance , User
from datetime import datetime, date
from decimal import Decimal
from django.utils.timezone import localtime, now  ,activate
from rest_framework.exceptions import NotFound
from django.db.models import Sum


class PunchInOutView(APIView):
    """
    View for users to punch in and punch out.
    """
    def post(self, request):
        activate('Asia/Karachi')
        user_id = request.data.get('user_id')  # Get user ID from request data
        if not user_id:
            return Response({"message": "User ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)  # Retrieve the user object
        except User.DoesNotExist:
            return Response({"message": "Invalid User ID."}, status=status.HTTP_400_BAD_REQUEST)

        today = date.today()
        # Get or create today's attendance
        attendance, created = Attendance.objects.get_or_create(user=user, date=today, defaults={'status': 'Present'})

        if not attendance.punch_in_time:
            # Punch In using local time
            punch_in_time = localtime(now()).time()
            print(punch_in_time)
            attendance.punch_in_time = punch_in_time
            attendance.save()
            return Response({"message": "Punched in successfully.", "punch_in_time": attendance.punch_in_time}, status=status.HTTP_200_OK)
        
        if not attendance.punch_out_time:
            # Punch Out using local time
            punch_out_time = localtime(now()).time()
            attendance.punch_out_time = punch_out_time
            punch_in = datetime.combine(today, attendance.punch_in_time)
            punch_out = datetime.combine(today, attendance.punch_out_time)
            hours_worked = hours_worked = Decimal((punch_out - punch_in).seconds) / Decimal(3600)  # Convert seconds to hours
            attendance.total_hours_day += hours_worked
            attendance.save()
            return Response({
                "message": "Punched out successfully.",
                "punch_out_time": attendance.punch_out_time,
                "hours_worked_today": hours_worked
            }, status=status.HTTP_200_OK)

        return Response({"message": "You have already punched out today."})


class AttendanceStatsView(APIView):
    """
    View for fetching user attendance statistics by user ID.
    """
    def get(self, request , user_id):
        
      
        
        # Validate user existence
        try:
            
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise NotFound({"message": "User not found."})

        today = date.today()

        # Calculate stats
        total_hours_month = Attendance.objects.filter(user=user, date__month=today.month).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        total_hours_week = Attendance.objects.filter(user=user, date__week=today.isocalendar()[1]).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        total_hours_year = Attendance.objects.filter(user=user, date__year=today.year).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        overtime = max(0, total_hours_month - 160)  # Assuming 160 working hours per month

        # Return attendance stats
        return Response({
            "user_id": user.id,
            "username": user.user_name,
            "total_hours_month": total_hours_month,
            "total_hours_week": total_hours_week,
            "total_hours_year": total_hours_year,
            "overtime_hours": overtime
        }, status=200)