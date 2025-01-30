import logging
from rest_framework.views import APIView
import pdb ;
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.contrib.auth.hashers import check_password

from ufcmsdb.models import CustomUser  # Ensure your custom user model is imported
from rest_framework.authtoken.models import Token  # Import Token model
from django.contrib.auth.hashers import check_password

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
                {"error": "Both user_name and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            # Ensure you are getting the User instance
            # pdb.set_trace()
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )

        if check_password(raw_password, user.password):
            token, created = Token.objects.get_or_create(user=user)  # Create or get token for user
            roles = user.role.all()
            designation = user.designation
            department = user.department

            roles_data = [{"id": role.id, "name": role.name} for role in roles]
            designation_data = {"id": designation.id, "name": designation.name} if designation else None
            department_data = {"id": department.id, "name": department.name} if department else None

            response_data = {
              
                "token": token.key,  # Include the token in the response
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials"}, 
                status=status.HTTP_403_FORBIDDEN
            )
