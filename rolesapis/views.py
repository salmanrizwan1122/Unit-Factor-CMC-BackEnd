from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from ufcmsdb.models import Role, Permission
import json
import logging

logger = logging.getLogger(__name__)

@method_decorator(csrf_exempt, name='dispatch')
class AddRoleView(APIView):
    # authentication_classes = [TokenAuthentication]
    # permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Print the Authorization header
            auth_header = request.headers.get('Authorization', None)
            logger.info(f"Authorization header: {auth_header}")

            # Authenticate the request
            user = request.user
            logger.info(f"User object: {user}")
            logger.info(f"User authenticated: {user.is_authenticated}")

            if not user.is_authenticated:
                logger.error("User not authenticated")
                return Response({"error": "Authentication required"}, status=401)

            # Parse request body
            data = json.loads(request.body)
            name = data.get("name")
            module_permissions = data.get("permissions", [])  # Array of module-permission mappings

            # Validate role name
            if not name:
                return Response({"error": "Role name is required"}, status=400)

            if not isinstance(module_permissions, list):
                return Response({"error": "Permissions must be a list"}, status=400)

            # Validate and collect permissions
            invalid_permissions = []
            valid_permissions = []

            for module_data in module_permissions:
                module = module_data.get("module")
                actions = module_data.get("actions", [])

                if not module or not isinstance(actions, list):
                    return Response(
                        {"error": "Each permission must include a 'module' and a list of 'actions'"},
                        status=400
                    )

                for action in actions:
                    permission = Permission.objects.filter(module=module, action=action).first()
                    if permission:
                        valid_permissions.append(permission.id)
                    else:
                        invalid_permissions.append({"module": module, "action": action})

            # Handle invalid permissions
            if invalid_permissions:
                return Response(
                    {"error": "Invalid permissions provided", "details": invalid_permissions},
                    status=400
                )

            # Create the role and associate permissions
            role = Role.objects.create(name=name)
            role.permissions.set(Permission.objects.filter(id__in=valid_permissions))

            # Track the creator
            creator = user
            logger.info(f"Role '{name}' created by: {creator.username}")

            return Response({"message": "Role created successfully", "role_id": role.id}, status=201)

        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return Response({"error": str(e)}, status=500)


class EditRoleView(APIView):
    def post(self, request, *args, **kwargs):
        try:
            # Get role ID from URL parameters
            role_id = kwargs.get('role_id')
            if not role_id:
                return JsonResponse({"error": "Role ID is required"}, status=400)

            # Parse the request body
            data = json.loads(request.body)
            name = data.get("name")
            module_permissions = data.get("permissions", [])

            # Fetch the role by ID
            role = Role.objects.filter(id=role_id).first()
            if not role:
                return JsonResponse({"error": "Role not found"}, status=404)

            # Validate role name (if provided)
            if name:
                role.name = name

            # Update permissions
            if module_permissions:
                # First, clear all existing permissions
                role.permissions.clear()

                invalid_permissions = []
                valid_permissions = []

                # Iterate over the modules and update the permissions
                for module_data in module_permissions:
                    module = module_data.get("module")
                    actions = module_data.get("actions", [])

                    if not module or not isinstance(actions, list):
                        return JsonResponse(
                            {"error": "Each permission must include a 'module' and a list of 'actions'"},
                            status=400
                        )

                    for action in actions:
                        permission = Permission.objects.filter(module=module, action=action).first()
                        if permission:
                            valid_permissions.append(permission.id)
                        else:
                            invalid_permissions.append({"module": module, "action": action})

                # Handle invalid permissions
                if invalid_permissions:
                    return JsonResponse(
                        {"error": "Invalid permissions provided", "details": invalid_permissions},
                        status=400
                    )

                # Add the new permissions to the role
                role.permissions.add(*Permission.objects.filter(id__in=valid_permissions))

            # Save the updated role
            role.save()

            return JsonResponse({"message": "Role updated successfully", "role_id": role.id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DeleteRoleView(APIView):
    def delete(self, request, *args, **kwargs):
        try:
            # Get role ID from URL parameters
            role_id = kwargs.get('role_id')
            if not role_id:
                return JsonResponse({"error": "Role ID is required"}, status=400)

            # Fetch the role by ID
            role = Role.objects.filter(id=role_id).first()
            if not role:
                return JsonResponse({"error": "Role not found"}, status=404)

            # Delete the role
            role.delete()

            return JsonResponse({"message": "Role deleted successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class GetAllRolesView(APIView):
    
    def get(self, request, *args, **kwargs):
        try:
            # Fetch all roles
            roles = Role.objects.all()

            # Serialize roles and their associated permissions grouped by module
            roles_data = []
            for role in roles:
                # Group permissions by module
                permissions_by_module = {}
                for perm in role.permissions.all():
                    module = perm.module
                    if module not in permissions_by_module:
                        permissions_by_module[module] = []
                    permissions_by_module[module].append({
                        "id": perm.id,
                        "action": perm.action.capitalize()
                    })

                roles_data.append({
                    "id": role.id,
                    "name": role.name,
                    "permissions": permissions_by_module  # Grouped by module
                })

            # Return the serialized data
            return JsonResponse({"roles": roles_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        try:
            # Fetch all roles
            roles = Role.objects.all()

            # Serialize roles data
            roles_data = []
            for role in roles:
                roles_data.append({
                    "id": role.id,
                    "name": role.name,
                    "permissions": [
                        {"id": perm.id, "name": perm.module  } for perm in role.permissions.all()
                    ]
                })

            return JsonResponse({"roles": roles_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)