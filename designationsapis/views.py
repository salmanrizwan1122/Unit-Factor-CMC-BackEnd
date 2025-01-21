from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from ufcmsdb.models import Designation, Department
import json

# View for creating a new Designation
class DesignationCreateView(View):
    def post(self, request):
        try:
            # Parse request body
            data = json.loads(request.body)

            # Validate input data
            department_id = data.get('department_id')
            designation_name = data.get('name')

            if not department_id or not designation_name:
                return JsonResponse({'error': 'Both department_id and name are required.'}, status=400)

            # Check if the department exists
            try:
                department = Department.objects.get(id=department_id)
            except ObjectDoesNotExist:
                return JsonResponse({'error': 'Department not found.'}, status=404)

            # Create the designation and store department name
            designation = Designation.objects.create(
                department=department,
                department_name=department.name,
                name=designation_name
            )

            return JsonResponse({'message': 'Designation created successfully.', 'designation_id': designation.id}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# View for fetching all Designations
class AllDesignationView(View):
    def get(self, request):
        try:
            # Fetch all designations
            designations = Designation.objects.all()

            # Serialize data
            designations_data = [{"id": desig.id, "name": desig.name, "department": desig.department_name} for desig in designations]

            return JsonResponse({"designations": designations_data}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# View for fetching a single Designation by ID
class DesignationByIdView(View):
    def get(self, request, designation_id):
        try:
            # Fetch designation by ID
            designation = Designation.objects.get(id=designation_id)

            return JsonResponse({
                "id": designation.id,
                "name": designation.name,
                "department": designation.department_name
            }, status=200)
        except Designation.DoesNotExist:
            return JsonResponse({"error": "Designation not found."}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


# View for updating an existing Designation
class EditDesignationView(View):
    def post(self, request, designation_id):
        try:
            # Parse request body
            data = json.loads(request.body)

            # Validate input data
            designation_name = data.get('name')
            department_id = data.get('department_id')

            if not designation_name or not department_id:
                return JsonResponse({'error': 'Both department_id and name are required for update.'}, status=400)

            # Check if the designation exists
            try:
                designation = Designation.objects.get(id=designation_id)
            except Designation.DoesNotExist:
                return JsonResponse({"error": "Designation not found."}, status=404)

            # Check if the new department exists
            try:
                department = Department.objects.get(id=department_id)
            except Department.DoesNotExist:
                return JsonResponse({'error': 'Department not found.'}, status=404)

            # Update designation
            designation.name = designation_name
            designation.department = department
            designation.department_name = department.name
            designation.save()

            return JsonResponse({'message': 'Designation updated successfully.', 'designation_id': designation.id}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format."}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# View for deleting a Designation
class DesignationDeleteView(View):
    def delete(self, request, designation_id):
        try:
            # Check if designation exists
            try:
                designation = Designation.objects.get(id=designation_id)
            except Designation.DoesNotExist:
                return JsonResponse({"error": "Designation not found."}, status=404)

            # Delete the designation
            designation.delete()

            return JsonResponse({"message": "Designation deleted successfully."}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
