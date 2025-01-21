from django.http import JsonResponse
from django.views import View
from ufcmsdb.models import User, Department, Designation, Role
import json
from django.core.exceptions import ObjectDoesNotExist

# Utility function to hash passwords
def hash_password(raw_password):
    from django.contrib.auth.hashers import make_password
    return make_password(raw_password)


class UserCreateView(View):
    def post(self, request):
        """Create a new user."""
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
                cnicno=data['cnicno']
            )

            user.role.set([role])

            return JsonResponse({'message': 'User created successfully', 'user_id': user.id ,'user_data': [{'Name':user.name, 'Email':user.email,'Age':user.age,'Address':user.address,'Department':user.department.name,'Designation':user.designation.name,'CNIC No':user.cnicno,'Role':role.name}]}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


class GetUserView(View):
    def get(self, request, user_id=None):
        """Retrieve user(s)."""
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
                })
            else:
                # Use prefetch_related to fetch roles, department, and designation efficiently
                users = User.objects.prefetch_related('role', 'department', 'designation').all()

                users_data = []
                for user in users:
                    user_roles = [{'id': role.id, 'name': role.name} for role in user.role.all()]
                    user_data = {
                        'id': user.id,
                        'name': user.name,
                        'email': user.email,
                        'age': user.age,
                        'address': user.address,
                        'department': {'id': user.department.id, 'name': user.department.name},  # Department with id and name
                        'designation': {'id': user.designation.id, 'name': user.designation.name},  # Designation with id and name
                        'roles': user_roles,  # Roles with id and name
                        'cnicno': user.cnicno
                    }
                    users_data.append(user_data)

                return JsonResponse({'users': users_data}, status=200)



        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class UpdateUserView(View):
    def post(self, request, user_id):
        """Update an existing user with provided data."""
        try:
            data = json.loads(request.body)  # Load the JSON data from request body
            user = User.objects.get(id=user_id)  # Get the user by the given user_id

            # Update the fields with the provided data, whether changed or unchanged
            if 'name' in data:
                user.name = data['name']
            if 'email' in data:
                # Ensure email is unique (exclude current user)
                if User.objects.filter(email=data['email']).exclude(id=user_id).exists():
                    return JsonResponse({'error': 'Email already exists'}, status=400)
                user.email = data['email']
            if 'password' in data:
                user.password = self.hash_password(data['password'])
            if 'age' in data:
                user.age = data['age']
            if 'address' in data:
                user.address = data['address']
            if 'department_id' in data:
                # Find department by ID
                department = Department.objects.filter(id=data['department_id']).first()
                if not department:
                    return JsonResponse({'error': 'Invalid department ID'}, status=400)
                user.department = department
            if 'designation_id' in data:
                # Find designation by ID
                designation = Designation.objects.filter(id=data['designation_id']).first()
                if not designation:
                    return JsonResponse({'error': 'Invalid designation ID'}, status=400)
                user.designation = designation
            if 'role_id' in data:
                # Find role by ID
                role = Role.objects.filter(id=data['role_id']).first()
                if not role:
                    return JsonResponse({'error': 'Invalid role ID'}, status=400)
                user.role.set([role])  # Assuming only one role is assigned
            if 'cnicno' in data:
                user.cnicno = data['cnicno']

            # Save the updated user data to the database
            user.save()

            return JsonResponse({'message': 'User updated successfully'}, status=200)

        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    def hash_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        return make_password(raw_password)

class DeleteUserView(View):
    def delete(self, request, user_id):
        """Delete an existing user."""
        try:
    

            userData = User.objects.get(id=user_id)
            user = User.objects.get(id=user_id)
            user.delete()
            return JsonResponse({'message': 'User deleted successfully' , 'user_data': [{'Name':userData.name, 'Email':userData.email,'Age':userData.age,'Address':userData.address,'Department':userData.department.name,'Designation':userData.designation.name,'CNIC No':userData.cnicno}]}, status=200)
        except User.DoesNotExist:
            return JsonResponse({'error': 'User not found'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
