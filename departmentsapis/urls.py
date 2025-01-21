from django.urls import path
from .views import DepartmentCreateView, AllDepartmentView, DepartmentByIdView, EditDepartmentView, DepartmentDeleteView

urlpatterns = [
    path('create/', DepartmentCreateView.as_view(), name='create_department'),  # Endpoint to create department
    path('get-all/', AllDepartmentView.as_view(), name='list_departments'),  # Endpoint to fetch all departments
    path('<int:department_id>/', DepartmentByIdView.as_view(), name='get_department'),  # Endpoint to fetch a specific department
    path('<int:department_id>/edit/', EditDepartmentView.as_view(), name='update_department'),  # Endpoint to update department
    path('<int:department_id>/delete/', DepartmentDeleteView.as_view(), name='delete_department'),  # Endpoint to delete department
]
