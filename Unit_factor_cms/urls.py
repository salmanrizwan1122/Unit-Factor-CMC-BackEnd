from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('roles/api/', include('rolesapis.urls')),  
    path('users/api/', include('usersapis.urls')),  
    path('departments/api/', include('departmentsapis.urls')),
    path('designations/api/', include('designationsapis.urls')),
    path('expense/api/', include('expenseapis.urls')),
    path('auth/api/', include('authapis.urls')),
    path('project/api/', include('projectsapi.urls')),  
    path('attendence/api/', include('attendenceapis.urls')),
    path('leave/api/', include('leavesapis.urls')),
    path('task/api/', include('tasksapis.urls')),
    path('api-token-auth/', obtain_auth_token),
]
