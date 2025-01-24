import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.hashers import check_password
from ufcmsdb.models import User  # Ensure your custom user model is imported
from rest_framework.authtoken.models import Token  # Import Token model

logger = logging.getLogger(__name__)

class LoginView(APIView):
    """
    Handle user login and generate token along with user details.
    No token is required to log in.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        # Get credentials from request
        user_name = request.data.get('user_name')
        raw_password = request.data.get('password')

        if not user_name or not raw_password:
            return Response(
                {"error": "Both user_name and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(user_name=user_name)
            print(user)  # This prints the user's string representation (probably user_name)
            print(user.id)  # This prints the user's ID
            print(user.email)  # This prints the user's email
        except User.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if check_password(raw_password, user.password):
            # Generate or get the token for the user
            token, created = Token.objects.get_or_create(user=user)

            # Prepare user-related details
            roles = user.role.all()
            designation = user.designation
            department = user.department

            roles_data = [{"id": role.id, "name": role.name} for role in roles]
            designation_data = {"id": designation.id, "name": designation.name} if designation else None
            department_data = {"id": department.id, "name": department.name} if department else None

            response_data = {
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "roles": roles_data,
                    "designation": designation_data,
                    "department": department_data,
                    "age": user.age,
                    "address": user.address,
                    "cnic": user.cnicno,  # Corrected from "cinic"
                    "joining_date": user.joining_date,
                },
                "token": token.key,  # Include the token in the response
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )
