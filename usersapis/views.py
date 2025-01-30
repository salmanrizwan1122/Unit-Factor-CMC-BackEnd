from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.db.models import Prefetch
import json
import logging
from ufcmsdb.models import CustomUser, Department, Designation, Role ,Project
from django.contrib.auth.hashers import make_password

logger = logging.getLogger(__name__)

class UserCreateView(APIView):
    """
    Handle user creation and generate token along with user details.
    Only authenticated users (with a valid token) can create new users.
    Track the creator of the user.
    """
    authentication_classes = [TokenAuthentication]  # Require token authentication
    permission_classes = [IsAuthenticated]  # Only authenticated users can create users

    def post(self, request):
        try:
            # Log the incoming request headers and body for debugging
            logger.info(f"Incoming request headers: {request.headers}")
            logger.info(f"Incoming request body: {request.body}")

            # Parse the request body
            data = json.loads(request.body)

            # Validate required fields
            required_fields = [
                'first_name', 'last_name', 'email', 'password', 'age', 'address',
                'department_id', 'designation_id', 'cnicno', 'role_id', 'username'
            ]
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            # Validate department
            department = Department.objects.filter(id=data['department_id']).first()
            if not department:
                return JsonResponse({'error': 'Invalid department ID'}, status=400)

            # Validate designation
            designation = Designation.objects.filter(id=data['designation_id']).first()
            if not designation:
                return JsonResponse({'error': 'Invalid designation ID'}, status=400)

            # Validate role
            role = Role.objects.filter(id=data['role_id']).first()
            if not role:
                return JsonResponse({'error': 'Invalid role ID'}, status=400)

            # Check if email already exists
            if CustomUser.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            # Check if username already exists
            if CustomUser.objects.filter(username=data['username']).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            # Create the user
            user = CustomUser.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                age=data['age'],
                address=data['address'],
                department=department,
                designation=designation,
                password=make_password(data['password']),  # Hash the password
                cnicno=data['cnicno'],
                username=data['username'],  # Use 'user_name' from the request
                created_by=request.user  # Track the creator
            )

            # Assign the role to the user
            user.role.set([role])

            # Log the created user details and the creator
            logger.info(f"User '{user.username}' created by: '{request.user.username}'")

            # Prepare the response data
            response_data = {
                'message': 'User created successfully',
                'user_id': user.id,
                'created_by': request.user.username,  # Include the creator's username
                'user_data': {
                    'Name': f"{user.first_name} {user.last_name}",  # Construct full name
                    'Email': user.email,
                    'Age': user.age,
                    'Address': user.address,
                    'Department': department.name,
                    'Designation': designation.name,
                    'CNIC No': user.cnicno,
                    'Role': role.name
                }
            }
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)
class GetUserView(APIView):
    def get(self, request, user_id=None):
        try:
            if user_id:
                # Retrieve a single user with related data
                user = CustomUser.objects.prefetch_related(
                    'role', 'department', 'designation', 
                    'projects',  # Projects where the user is a team member
                    Prefetch('led_projects', queryset=Project.objects.prefetch_related('team_members'))  # Projects the user leads
                ).get(id=user_id)

                # Prepare the response for led projects
                led_projects = [
                    {
                        'id': project.id,
                        'name': project.name,
                        'deadline': project.deadline,
                        'total_tasks': project.total_tasks,
                        'description': project.description,
                        'team_members': [
                            {'id': member.id, 'name': f"{member.first_name} {member.last_name}"}
                            for member in project.team_members.all()
                        ]
                    }
                    for project in user.led_projects.all()
                ]

                # Prepare the response for team projects
                team_projects = [
                    {
                        'id': project.id,
                        'name': project.name,
                        'deadline': project.deadline,
                        'total_tasks': project.total_tasks,
                        'description': project.description,
                        'leader': {
                            'id': project.leader.id,
                            'name': f"{project.leader.first_name} {project.leader.last_name}"
                        } if project.leader else None
                    }
                    for project in user.projects.all()
                ]

                return JsonResponse({
                    'id': user.id,
                    'name': f"{user.first_name} {user.last_name}",  # Construct full name
                    'email': user.email,
                    'age': user.age,
                    'address': user.address,
                    'department': {'id': user.department.id, 'name': user.department.name} if user.department else None,
                    'designation': {'id': user.designation.id, 'name': user.designation.name} if user.designation else None,
                    'roles': [{'id': role.id, 'name': role.name} for role in user.role.all()],
                    'cnicno': user.cnicno,
                    'created_by': {
                            'id': user.created_by.id,
                            'name': f"{user.created_by.first_name} {user.created_by.last_name}"
                        } if user.created_by else None,
                    'team_projects': team_projects,  # Will be an empty list if no projects
                    'led_projects': led_projects  # Will be an empty list if no projects
                }, status=200)

            else:
                # Retrieve all users with related data
                users = CustomUser.objects.prefetch_related(
                    'role', 'department', 'designation', 
                    'projects',  # Projects where the user is a team member
                    Prefetch('led_projects', queryset=Project.objects.prefetch_related('team_members'))  # Projects the user leads
                ).all()

                users_data = []
                for user in users:
                    # Prepare the response for led projects
                    led_projects = [
                        {
                            'id': project.id,
                            'name': project.name,
                            'deadline': project.deadline,
                            'total_tasks': project.total_tasks,
                            'description': project.description,
                            'team_members': [
                                {'id': member.id, 'name': f"{member.first_name} {member.last_name}"}
                                for member in project.team_members.all()
                            ]
                        }
                        for project in user.led_projects.all()
                    ]

                    # Prepare the response for team projects
                    team_projects = [
                        {
                            'id': project.id,
                            'name': project.name,
                            'deadline': project.deadline,
                            'total_tasks': project.total_tasks,
                            'description': project.description,
                            'leader': {
                                'id': project.leader.id,
                                'name': f"{project.leader.first_name} {project.leader.last_name}"
                            } if project.leader else None
                        }
                        for project in user.projects.all()
                    ]

                    users_data.append({
                        'id': user.id,
                        'name': f"{user.first_name} {user.last_name}",  # Construct full name
                        'email': user.email,
                        'age': user.age,
                        'address': user.address,
                        'department': {'id': user.department.id, 'name': user.department.name} if user.department else None,
                        'designation': {'id': user.designation.id, 'name': user.designation.name} if user.designation else None,
                        'roles': [{'id': role.id, 'name': role.name} for role in user.role.all()],
                        'cnicno': user.cnicno,
                        'created_by': {
                            'id': user.created_by.id,
                            'name': f"{user.created_by.first_name} {user.created_by.last_name}"
                        } if user.created_by else None,
                        'team_projects': team_projects,  # Will be an empty list if no projects
                        'led_projects': led_projects  # Will be an empty list if no projects
                    })

                return JsonResponse({'users': users_data}, status=200)

        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class UpdateUserView(APIView):
    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            user = CustomUser.objects.get(id=user_id)

            if 'first_name' in data:
                user.first_name = data['first_name']
            if 'last_name' in data:
                user.last_name = data['last_name']
            if 'email' in data:
                if CustomUser.objects.filter(email=data['email']).exclude(id=user_id).exists():
                    return JsonResponse({'error': 'Email already exists'}, status=400)
                user.email = data['email']
            if 'password' in data:
                user.set_password(data['password'])  # Hash the password
            if 'age' in data:
                user.age = data['age']
            if 'address' in data:
                user.address = data['address']
            if 'department_id' in data:
                department = Department.objects.filter(id=data['department_id']).first()
                if not department:
                    return JsonResponse({'error': 'Invalid department ID'}, status=400)
                user.department = department
            if 'designation_id' in data:
                designation = Designation.objects.filter(id=data['designation_id']).first()
                if not designation:
                    return JsonResponse({'error': 'Invalid designation ID'}, status=400)
                user.designation = designation
            if 'role_id' in data:
                role = Role.objects.filter(id=data['role_id']).first()
                if not role:
                    return JsonResponse({'error': 'Invalid role ID'}, status=400)
                user.role.set([role])
            if 'cnicno' in data:
                user.cnicno = data['cnicno']

            user.save()

            return JsonResponse({
                'message': 'User updated successfully',
            }, status=200)

        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class DeleteUserView(APIView):
    """Delete an existing user (Token Required)."""
  

    def delete(self, request, user_id):
        try:
           
            user = CustomUser.objects.get(id=user_id)
            user.delete()
            return JsonResponse({
                'message': 'User deleted successfully',
                
            }, status=200)
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
