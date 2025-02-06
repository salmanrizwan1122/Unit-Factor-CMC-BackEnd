from django.urls import path
from .views import TaskCreateView , GetTaskByIdView , GetAllTasksView ,UpdateTaskStatusView , DeleteTaskView

urlpatterns = [
    path('create/', TaskCreateView.as_view(), name='task-create'),  
    path('<int:task_id>/', GetTaskByIdView.as_view(), name='get-task'),  
    path('get-all/', GetAllTasksView.as_view(), name='all-task'),  
    path('update-status/', UpdateTaskStatusView.as_view(), name='update-task'), 
    path('<int:task_id>/delete/',DeleteTaskView.as_view(), name = 'delete-task' ) # Endpoint to fetch all roles
 


]
