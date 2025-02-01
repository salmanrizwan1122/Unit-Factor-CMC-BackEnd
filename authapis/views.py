import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.core.mail import send_mail
from django.utils.timezone import now
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from ufcmsdb.models import CustomUser, Project, Attendance, Leave , PasswordResetOTP
from rest_framework.authtoken.models import Token
from datetime import date
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.conf import settings  # Import settings to use email configuration
import random  # Import random for OTP generation


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



class ForgotPasswordView(APIView):
    """
    Handle forgot password requests by sending an OTP to the user's email.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"error": "User with this email does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Generate OTP
        otp = random.randint(100000, 999999)
        PasswordResetOTP.objects.update_or_create(
        email=user.email,  # Use email instead of user
        defaults={"otp": otp, "created_at": now()}
)

        # Send OTP via email
        send_mail(
            "Password Reset OTP",
            f"Your OTP for password reset is {otp}. This OTP is valid for 10 minutes.",
            settings.DEFAULT_FROM_EMAIL,
            [email],
            fail_silently=False,
        )

        return Response({"message": "OTP has been sent to your email."}, status=status.HTTP_200_OK)

class ResetPasswordView(APIView):
    """
    Handle OTP verification and password reset.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")
        new_password = request.data.get("new_password")

        if not email or not otp or not new_password:
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(email=email)
            otp_record = PasswordResetOTP.objects.get(email=email, otp=otp)  # Use email instead of user
        except (CustomUser.DoesNotExist, PasswordResetOTP.DoesNotExist):
            return Response({"error": "Invalid OTP or email."}, status=status.HTTP_400_BAD_REQUEST)

        # Reset password
        user.password = make_password(new_password)
        user.save()

        # Delete OTP record after successful password reset
        otp_record.delete()

        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
