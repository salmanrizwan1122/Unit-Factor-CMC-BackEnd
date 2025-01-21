from django.urls import path
from .views import UserCreateView, GetUserView, UpdateUserView, DeleteUserView

urlpatterns = [
    path('create/', UserCreateView.as_view(), name='user-create'),  # Create a user
    path('get-all/', GetUserView.as_view(), name='user-list'),         # Retrieve all users
    path('<int:user_id>/', GetUserView.as_view(), name='user-detail'),  # Retrieve a single user by ID
    path('<int:user_id>/edit/', UpdateUserView.as_view(), name='user-update'),  # Update a user by ID
    path('<int:user_id>/delete/', DeleteUserView.as_view(), name='user-delete'),  # Delete a user by ID
]
