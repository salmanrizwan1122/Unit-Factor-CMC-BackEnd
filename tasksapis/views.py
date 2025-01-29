from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ufcmsdb.models import Task, Project, User
from rest_framework.exceptions import NotFound
from datetime import datetime

class TaskCreateView(APIView):
  
    def post(self, request):
        project_id = request.data.get('project_id')  # Get project ID from request data
        name = request.data.get('name')  # Get task name from request data
        description = request.data.get('description', '')  # Get task description from request data
        assigned_to_id = request.data.get('assigned_to')  # Get user ID of the assignee from request data
        status = request.data.get('status', 'Pending')  # Get task status from request data (default to Pending)
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
            assigned_to = User.objects.get(id=assigned_to_id)
        except User.DoesNotExist:
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
            status=status,
            priority=priority,
            due_date=due_date
        )
        task.save()

        return Response({
            "message": "Task created successfully.",
            "task_id": task.id,
            "task_name": task.name,
            "assigned_to": task.assigned_to.user_name,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date
        }, status=status.HTTP_201_CREATED)
class GetTaskByIdView(APIView):
    """
    View to get a task by its ID.
    """
    def get(self, request, task_id):
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
            "assigned_to": task.assigned_to.user_name if task.assigned_to else None,
            "status": task.status,
            "priority": task.priority,
            "due_date": task.due_date,
            "created_at": task.created_at,
            "updated_at": task.updated_at,
        }
        return Response({"task": task_data}, status=status.HTTP_200_OK)

class GetAllTasksView(APIView):
    """
    View to get all tasks.
    """
    def get(self, request):
        tasks = Task.objects.all().values(
            'id', 'project__name', 'name', 'description', 'assigned_to__user_name', 
            'status', 'priority', 'due_date', 'created_at', 'updated_at'
        )
        return Response({"tasks": list(tasks)}, status=status.HTTP_200_OK)
    


class DeleteTaskView(APIView):
    
    def delete(self, request, task_id):
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
    def post(self, request):
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
            updated_by = User.objects.get(id=updated_by_id)
        except User.DoesNotExist:
            return Response({"message": "Invalid Updated By ID."}, status=status.HTTP_400_BAD_REQUEST)

        task.status = new_status
        task.updated_by = updated_by
        task.save()

        return Response({"message": "Task status updated successfully, updated by {}.".format(updated_by.user_name)}, status=status.HTTP_200_OK)