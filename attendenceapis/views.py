import json
from datetime import datetime, date
from decimal import Decimal

from django.utils.timezone import localtime, now, activate
from django.db.models import Sum
from django.core.exceptions import ObjectDoesNotExist
from django.utils.dateparse import parse_date

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied

from ufcmsdb.models import Attendance, CustomUser


# Function to check if a user has permission based on roles
def user_has_permission(user, action, module):
    """Check if a user has a given permission on a module."""
    return user.role.filter(permissions__action=action, permissions__module=module).exists()


class PunchInOutView(APIView):
    """
    View for authenticated users to punch in and punch out.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        activate('Asia/Karachi')
        user = request.user  # Get authenticated user

        today = date.today()
        attendance, created = Attendance.objects.get_or_create(
            user=user, date=today, defaults={'status': 'Present'}
        )

        if not attendance.punch_in_time:
            # Punch In
            attendance.punch_in_time = localtime(now()).time()
            attendance.save()
            return Response({
                "message": "Punched in successfully.",
                "punch_in_time": attendance.punch_in_time
            }, status=status.HTTP_200_OK)

        if not attendance.punch_out_time:
            # Punch Out
            attendance.punch_out_time = localtime(now()).time()
            punch_in = datetime.combine(today, attendance.punch_in_time)
            punch_out = datetime.combine(today, attendance.punch_out_time)
            hours_worked = Decimal((punch_out - punch_in).seconds) / Decimal(3600)
            attendance.total_hours_day += hours_worked
            attendance.save()
            return Response({
                "message": "Punched out successfully.",
                "punch_out_time": attendance.punch_out_time,
                "hours_worked_today": hours_worked
            }, status=status.HTTP_200_OK)

        return Response({"message": "You have already punched out today."}, status=status.HTTP_400_BAD_REQUEST)


class UserAttendanceStatsView(APIView):
    """
    View to retrieve an authenticated user's own attendance stats.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        today = date.today()

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

        attendance_records = Attendance.objects.filter(user=user).values('date', 'punch_in_time', 'punch_out_time')

        return Response({
            "user_id": user.id,
            "username": user.username,
            "total_hours_month": total_hours_month,
            "total_hours_week": total_hours_week,
            "total_hours_year": total_hours_year,
            "overtime_hours": overtime,
            "attendance_records": list(attendance_records)
        }, status=status.HTTP_200_OK)


class AllAttendanceStatsView(APIView):
    """
    View to retrieve all users' attendance records.
    Only users with "read" permission for "attendance" can access this.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Check if the user has 'read' permission for attendance
        if not user_has_permission(user, "read", "attendance"):
            raise PermissionDenied("You do not have permission to view all attendance records.")

        today = date.today()

        total_hours_month = Attendance.objects.filter(date__month=today.month).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        total_hours_week = Attendance.objects.filter(date__week=today.isocalendar()[1]).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        total_hours_year = Attendance.objects.filter(date__year=today.year).aggregate(
            Sum('total_hours_day')
        )['total_hours_day__sum'] or 0

        attendance_records = Attendance.objects.select_related('user').values(
            'user__id', 'user__username', 'date', 'punch_in_time', 'punch_out_time', 'total_hours_day'
        )

        return Response({
            "total_hours_month": total_hours_month,
            "total_hours_week": total_hours_week,
            "total_hours_year": total_hours_year,
            "attendance_records": list(attendance_records)
        }, status=status.HTTP_200_OK)
