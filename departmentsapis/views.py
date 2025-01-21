from django.http import JsonResponse
from django.views import View
from ufcmsdb.models import Department , Designation
import json


class DepartmentCreateView(View):
    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)

            # Perform manual validation
            if not data.get('name'):
                return JsonResponse({'error': 'Department name is required'}, status=400)

            # Check if the department name already exists
            if Department.objects.filter(name=data['name']).exists():
                return JsonResponse({'error': 'Department with this name already exists'}, status=400)

            # Create the department
            department = Department.objects.create(name=data['name'])

            return JsonResponse({'message': 'Department created successfully', 'department_id': department.id}, status=201)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

class AllDepartmentView(View):
    def get(self, request):
        try:
            # Fetch all departments and their designations
            departments = Department.objects.all()

            # Serialize data
            departments_data = []
            for dept in departments:
                # Get designations for each department
                designations = Designation.objects.filter(department=dept)
                designations_data = [{"id": desig.id, "name": desig.name} for desig in designations]

                departments_data.append({
                    "id": dept.id,
                    "name": dept.name,
                    "designations": designations_data  # Include designations
                })

            return JsonResponse({"departments": departments_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class DepartmentByIdView(View):
    def get(self, request, department_id):
        try:
            # Fetch department by ID
            department = Department.objects.get(id=department_id)

            return JsonResponse({
                "id": department.id,
                "name": department.name
            }, status=200)
        except Department.DoesNotExist:
            return JsonResponse({"error": "Department not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class EditDepartmentView(View):
    def post(self, request, department_id):
        try:
            # Parse request body
            data = json.loads(request.body)

            # Check if the department name is provided
            if not data.get('name'):
                return JsonResponse({"error": "Department name is required"}, status=400)

            # Check if department exists
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Update department name
            department.name = data['name']
            department.save()

            return JsonResponse({"message": "Department updated successfully", "department_id": department.id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class DepartmentDeleteView(View):
    def delete(self, request, department_id):
        try:
            # Check if department exists
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({"error": "Department not found"}, status=404)

            # Delete the department
            department.delete()

            return JsonResponse({"message": "Department deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
