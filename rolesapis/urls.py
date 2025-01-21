from django.urls import path
from .views import AddRoleView, GetAllRolesView, DeleteRoleView, EditRoleView

urlpatterns = [
    path('create/', AddRoleView.as_view(), name='add_role'),  # Endpoint to create a role
    path('get-all/', GetAllRolesView.as_view(), name='get_all_roles'),  # Endpoint to fetch all roles
    path('<int:role_id>/edit/', EditRoleView.as_view(), name='edit_role'),  # Endpoint to edit a role
    path('<int:role_id>/delete/', DeleteRoleView.as_view(), name='delete_role'),  # Endpoint to delete a role
]
