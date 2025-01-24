from django.urls import path
from .views import CreateProjectView, GetProjectDetailsView , DeleteProjectView , GetAllProjectsView , UpdateProjectView

urlpatterns = [
    path('create/', CreateProjectView.as_view(), name='create_project'),
    path('<int:project_id>/', GetProjectDetailsView.as_view(), name='project-detail'),  # Retrieve a single user by ID
    path('get-all/', GetAllProjectsView.as_view(), name='project-list'),  # Retrieve a single user by ID
    path('<int:project_id>/delete/', DeleteProjectView.as_view(), name='project-delete'),
    path('<int:project_id>/edit/', UpdateProjectView.as_view(), name='project-update'),  

]
