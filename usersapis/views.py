from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from ufcmsdb.models import User, Department, Designation, Role
import json
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.hashers import make_password
from rest_framework.permissions import AllowAny
# Utility function to hash passwords
def hash_password(raw_password):
    return make_password(raw_password)


class UserCreateView(APIView):
    print("inside user create view")
    
   

    
    print(User.objects.filter(id=13).exists())

    def post(self, request):
        print("inside user create ")
        print(request.auth)
        try:
            data = json.loads(request.body)
            required_fields = ['name', 'email', 'password', 'age', 'address', 'department_id', 'designation_id', 'cnicno', 'role_id']
            for field in required_fields:
                if not data.get(field):
                    return JsonResponse({'error': f'{field} is required'}, status=400)

            department = Department.objects.filter(id=data['department_id']).first()
            if not department:
                return JsonResponse({'error': 'Invalid department ID'}, status=400)

            designation = Designation.objects.filter(id=data['designation_id']).first()
            if not designation:
                return JsonResponse({'error': 'Invalid designation ID'}, status=400)

            role = Role.objects.filter(id=data['role_id']).first()
            if not role:
                return JsonResponse({'error': 'Invalid role ID'}, status=400)

            if User.objects.filter(email=data['email']).exists():
                return JsonResponse({'error': 'Email already exists'}, status=400)

            user = User.objects.create(
                name=data['name'],
                email=data['email'],
                age=data['age'],
                address=data['address'],
                department=department,
                designation=designation,
                password=hash_password(data['password']),
                cnicno=data['cnicno'],
                user_name = data['user_name']
            )

            user.role.set([role])

            # Track the user who performed the action
        

            return JsonResponse({
                'message': 'User created successfully',
                'user_id': user.id,
             
                'user_data': {
                    'Name': user.name,
                    'Email': user.email,
                    'Age': user.age,
                    'Address': user.address,
                    'Department': department.name,
                    'Designation': designation.name,
                    'CNIC No': user.cnicno,
                    'Role': role.name
                }
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class GetUserView(APIView):
    """Retrieve user(s)."""

    def get(self, request, user_id=None):
        try:
            if user_id:
                user = User.objects.get(id=user_id)
                return JsonResponse({
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'age': user.age,
                    'address': user.address,
                    'department': {'id': user.department.id, 'name': user.department.name},
                    'designation': {'id': user.designation.id, 'name': user.designation.name},
                    'roles': [{'id': role.id, 'name': role.name} for role in user.role.all()],
                    'cnicno': user.cnicno
                }, status=200)
            else:
                users = User.objects.prefetch_related('role', 'department', 'designation').all()
                users_data = []
                for user in users:
                    user_roles = [{'id': role.id, 'name': role.name} for role in user.role.all()]
                    users_data.append({
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'age': user.age,
                        'address': user.address,
                        'department': {'id': user.department.id, 'name': user.department.name},
                        'designation': {'id': user.designation.id, 'name': user.designation.name},
                        'roles': user_roles,
                        'cnicno': user.cnicno
                    })
                return JsonResponse({'users': users_data}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class UpdateUserView(APIView):
    """Update an existing user (Token Required)."""
   

    def post(self, request, user_id):
        try:
            data = json.loads(request.body)
            user = User.objects.get(id=user_id)

         

            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                if User.objects.filter(email=data['email']).exclude(id=user_id).exists():
                    return JsonResponse({'error': 'Email already exists'}, status=400)
                user.email = data['email']
            if 'password' in data:
                user.password = hash_password(data['password'])
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

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class DeleteUserView(APIView):
    """Delete an existing user (Token Required)."""
  

    def delete(self, request, user_id):
        try:
           
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({
                'message': 'User deleted successfully',
                
            }, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
