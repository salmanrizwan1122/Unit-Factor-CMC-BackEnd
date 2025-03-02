from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ufcmsdb.models import Task, Project, CustomUser
from rest_framework.exceptions import NotFound
from datetime import datetime
from django.http import JsonResponse
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

class TaskCreateView(APIView):
    authentication_classes = [TokenAuthentication]  
    permission_classes = [IsAuthenticated]  

    def post(self, request):
        user = request.user  # Get the authenticated user

        # Check if the user has permission to create a task
        has_permission = user.role.filter(permissions__action="create", permissions__module="task_management").exists()
        
        if not has_permission:
            return JsonResponse({'error': 'You do not have permission to create a task.'}, status=403)
            
        project_id = request.data.get('project_id')  # Get project ID from request data
        name = request.data.get('name')  # Get task name from request data
        description = request.data.get('description', '')  # Get task description from request data
        assigned_to_id = request.data.get('assigned_to')  # Get user ID of the assignee from request data
        task_status = request.data.get('status', 'Pending')  # Get task status from request data (default to Pending)
        priority = request.data.get('priority', 'Medium')  # Get task priority from request data (default to Medium)
        due_date = request.data.get('due_date')  # Get task due date from request data

        # Validate required fields
        if not project_id or not name or not assigned_to_id:
            return Response({"message": "Project ID, task name, and assigned user ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate existence of related project and user
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"message": "Invalid Project ID."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            assigned_to = CustomUser.objects.get(id=assigned_to_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Invalid User ID for assignee."}, status=status.HTTP_400_BAD_REQUEST)

        # Validate due date format
        try:
            due_date = datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None
        except ValueError:
            return Response({"message": "Invalid due date format. Use YYYY-MM-DD."}, status=status.HTTP_400_BAD_REQUEST)

        # Create and save new task
        task = Task(
            project=project,
            name=name,
            description=description,
            assigned_to=assigned_to,
            status=task_status,
            priority=priority,
            due_date=due_date
        )
        task.save()
        return Response({
            "message": "Task created successfully.",
            "task_id": task.id,
            "task_name": task.name,
            "assigned_to": task.assigned_to.username,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date
        }, status=status.HTTP_201_CREATED)




class GetTaskByIdView(APIView):
    

    def get(self, request, task_id):
        user = request.user  # Get the authenticated user

        # Check if the user has permission to read a task
        has_permission = user.role.filter(permissions__action="read", permissions__module="task_management").exists()
        
        if not has_permission:
            return JsonResponse({'error': 'You do not have permission to view this task.'}, status=403)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound({"message": "Task not found."})

        task_data = {
            "task_id": task.id,
            "project_id": task.project.id,
            "project_name": task.project.name,
            "name": task.name,
            "description": task.description,
            "assigned_to": task.assigned_to.username if task.assigned_to else None,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
        return Response({"task": task_data}, status=status.HTTP_200_OK)

class GetAllTasksView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # Get the authenticated user

        # Check if the user has permission to read tasks
        has_permission = user.role.filter(permissions__action="read", permissions__module="task_management").exists()
        
        if not has_permission:
            return JsonResponse({'error': 'You do not have permission to view tasks.'}, status=403)
        
        tasks = Task.objects.all().values(
            'id', 'project__name', 'name', 'description', 'assigned_to__username', 
            'status', 'priority', 'due_date', 'created_at', 'updated_at'
        )
        return Response({"tasks": list(tasks)}, status=status.HTTP_200_OK)
class DeleteTaskView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def delete(self, request, task_id):
        user = request.user  # Get the authenticated user

        # Check if the user has permission to delete a task
        has_permission = user.role.filter(permissions__action="delete", permissions__module="task_management").exists()
        
        if not has_permission:
            return JsonResponse({'error': 'You do not have permission to delete this task.'}, status=403)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound({"message": "Task not found."})

        task.delete()
        return Response({"message": "Task deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

class UpdateTaskStatusView(APIView):
    """
    View to update the status of a task.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user  # Get the authenticated user

        # Check if the user has permission to update a task
        has_permission = user.role.filter(permissions__action="update", permissions__module="task_management").exists()
        
        if not has_permission:
            return JsonResponse({'error': 'You do not have permission to update this task.'}, status=403)

        task_id = request.data.get('task_id')
        new_status = request.data.get('status')
        updated_by_id = request.data.get('updated_by')

        if not task_id or not new_status or not updated_by_id:
            return Response({"message": "Task ID, status, and updated by ID are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            task = Task.objects.get(id=task_id)
        except Task.DoesNotExist:
            raise NotFound({"message": "Task not found."})

        try:
            updated_by = CustomUser.objects.get(id=updated_by_id)
        except CustomUser.DoesNotExist:
            return Response({"message": "Invalid Updated By ID."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status
        task.updated_by = updated_by
        task.save()

        return Response({"message": "Task status updated successfully, updated by {}.".format(updated_by.username)}, status=status.HTTP_200_OK)

