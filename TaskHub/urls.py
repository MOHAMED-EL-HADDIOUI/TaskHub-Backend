from django.contrib import admin
from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from projects.views import create_project, project_list, get_project_details, update_project, delete_project
from tasks.views import (
    create_task,
    task_list,
    update_task,
    delete_task,
    register_user, login_user, logout_user,
    UserProfileView, UserListView, get_tasks_assigned_to_user
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/profile/', UserProfileView.as_view(), name='user_profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('tasks/assignedto/', get_tasks_assigned_to_user, name='get_tasks_assigned_to_user'),
    # Project URLs
    path('projects/<int:project_id>/', get_project_details, name='get_project_details'),
    path('projects/add', create_project, name='create_project'),  # Create a project
    path('projects/<int:project_id>/update/', update_project, name='update_project'),  # Update a specific project
    path('projects/<int:project_id>/delete/', delete_project, name='delete_project'),  # Delete a specific task
    path('projects/', project_list, name='project_list'),  # List all projects
    # Task URLs
    path('projects/<int:project_id>/tasks/', task_list, name='task_list'),  # List tasks for a project
    path('projects/<int:project_id>/tasks/create/', create_task, name='create_task'),  # Create a task for a project
    path('tasks/<int:task_id>/update/', update_task, name='update_task'),  # Update a specific task
    path('tasks/<int:task_id>/delete/', delete_task, name='delete_task'),  # Delete a specific task
    # User Role Management
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('logout/', logout_user, name='logout_user'),
    path('token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
