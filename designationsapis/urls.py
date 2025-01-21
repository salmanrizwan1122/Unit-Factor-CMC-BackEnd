from django.urls import path
from .views import DesignationCreateView, AllDesignationView, DesignationByIdView, EditDesignationView, DesignationDeleteView

urlpatterns = [
    path('create/', DesignationCreateView.as_view(), name='create-designation'),
    path('get-all/', AllDesignationView.as_view(), name='all-designations'),  # List all designations
    path('<int:designation_id>/', DesignationByIdView.as_view(), name='designation-by-id'),  # Fetch a single designation by ID
    path('<int:designation_id>/edit/', EditDesignationView.as_view(), name='edit-designation'),  # Update a designation
    path('<int:designation_id>/delete/', DesignationDeleteView.as_view(), name='delete-designation'),  # Delete a designation
]
