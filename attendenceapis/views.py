from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils.timezone import now
from datetime import timedelta
from ufcmsdb.models import Attendance
from datetime import datetime, date


class PunchInOutView(APIView):
    """
    View for users to punch in and punch out.
    """
    def post(self, request):
        user = request.user
        today = date.today()

        # Get or create today's attendance
        attendance, created = Attendance.objects.get_or_create(user=user, date=today, defaults={'status': 'Present'})

        if not attendance.punch_in_time:
            # Punch In
            attendance.punch_in_time = now().time()
            attendance.save()
            return Response({"message": "Punched in successfully.", "punch_in_time": attendance.punch_in_time}, status=status.HTTP_200_OK)
        
        if not attendance.punch_out_time:
            # Punch Out
            attendance.punch_out_time = now().time()
            punch_in = datetime.combine(today, attendance.punch_in_time)
            punch_out = datetime.combine(today, attendance.punch_out_time)
            hours_worked = (punch_out - punch_in).seconds / 3600  # Convert seconds to hours
            attendance.total_hours_day += hours_worked
            attendance.save()
            return Response({
                "message": "Punched out successfully.",
                "punch_out_time": attendance.punch_out_time,
                "hours_worked_today": hours_worked
            }, status=status.HTTP_200_OK)

        return Response({"message": "You have already punched out today."}, status=status.HTTP_400_BAD_REQUEST)

class AttendanceStatsView(APIView):
    """
    View for fetching user attendance statistics.
    """
    def get(self, request):
        user = request.user
        today = date.today()

        # Calculate stats
        total_hours_month = Attendance.objects.filter(user=user, date__month=today.month).aggregate(models.Sum('total_hours_day'))['total_hours_day__sum'] or 0
        total_hours_week = Attendance.objects.filter(user=user, date__week=today.isocalendar()[1]).aggregate(models.Sum('total_hours_day'))['total_hours_day__sum'] or 0
        total_hours_year = Attendance.objects.filter(user=user, date__year=today.year).aggregate(models.Sum('total_hours_day'))['total_hours_day__sum'] or 0
        overtime = max(0, total_hours_month - 160)  # Assuming 160 working hours per month

        return Response({
            "total_hours_month": total_hours_month,
            "total_hours_week": total_hours_week,
            "total_hours_year": total_hours_year,
            "overtime_hours": overtime
        }, status=status.HTTP_200_OK)
