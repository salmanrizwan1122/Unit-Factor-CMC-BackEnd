import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.hashers import check_password
from ufcmsdb.models import CustomUser, Project, Attendance, Leave
from rest_framework.authtoken.models import Token
from datetime import date
from django.db.models import Sum

logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    Handle user login and generate token along with user details.
    No token is required to log in.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Get credentials from request
        email = request.data.get('email')
        raw_password = request.data.get('password')

        if not email or not raw_password:
            return Response(
                {"error": "Both email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if check_password(raw_password, user.password):
            # Create or get token for user
            token, created = Token.objects.get_or_create(user=user)

            # Get user-related data
            roles = user.role.all()
            designation = user.designation
            department = user.department
            projects = user.projects.all()
            led_projects = user.led_projects.all()

            # Attendance Data
            today = date.today()
            attendance_today = Attendance.objects.filter(user=user, date=today).first()
            punch_in_time = attendance_today.punch_in_time if attendance_today else None
            punch_out_time = attendance_today.punch_out_time if attendance_today else None

            # Attendance Statistics
            total_hours_month = Attendance.objects.filter(user=user, date__month=today.month).aggregate(
                Sum('total_hours_day')
            )['total_hours_day__sum'] or 0

            total_hours_week = Attendance.objects.filter(user=user, date__week=today.isocalendar()[1]).aggregate(
                Sum('total_hours_day')
            )['total_hours_day__sum'] or 0

            total_hours_year = Attendance.objects.filter(user=user, date__year=today.year).aggregate(
                Sum('total_hours_day')
            )['total_hours_day__sum'] or 0

            overtime_hours = max(0, total_hours_month - 160)  # Assuming 160 working hours per month

            attendance_records = Attendance.objects.filter(user=user).values('date', 'punch_in_time', 'punch_out_time')

            # Leave Data
            leaves = Leave.objects.filter(user=user)
            leave_data = [
                {"id": leave.id, "type": leave.leave_type, "status": leave.status, "date": leave.leave_from}
                for leave in leaves
            ]

            # Get permissions assigned to the roles
            permissions = set()
            for role in roles:
                role_permissions = role.permissions.all()
                permissions.update(role_permissions)

            permissions_data = [{"id": perm.id, "action": perm.action, "module": perm.module} for perm in permissions]

            # Preparing roles, designation, department, and projects data
            roles_data = [{"id": role.id, "name": role.name} for role in roles]
            designation_data = {"id": designation.id, "name": designation.name} if designation else None
            department_data = {"id": department.id, "name": department.name} if department else None

            projects_data = [
                {"id": project.id, "name": project.name, "deadline": project.deadline, "total_tasks": project.total_tasks}
                for project in projects
            ]

            led_projects_data = [
                {"id": project.id, "name": project.name, "deadline": project.deadline, "total_tasks": project.total_tasks}
                for project in led_projects
            ]

            response_data = {
                "token": token.key,
                "user": {
                    "id": user.id,
                    "email": user.email,
                    "roles": roles_data,
                    "designation": designation_data,
                    "department": department_data,
                    "projects": projects_data,
                    "led_projects": led_projects_data,
                    "punch_in_time": punch_in_time,
                    "punch_out_time": punch_out_time,
                    "attendance": {
                        "total_hours_month": total_hours_month,
                        "total_hours_week": total_hours_week,
                        "total_hours_year": total_hours_year,
                        "overtime_hours": overtime_hours,
                        "records": list(attendance_records)
                    },
                    "leave_data": leave_data,
                    "permissions": permissions_data
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )
