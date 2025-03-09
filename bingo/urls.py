# Django Imports
from django.urls import path

# DRF Imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

# Import Views from .views Module
from .views import (
    get_user_profile, register_user, login_user, tasks, pending_tasks,
    complete_task, leaderboard, update_user_profile, check_developer_role
)

# URL Patterns
urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('tasks/', tasks, name='tasks'),
    path('pending-tasks/', pending_tasks, name='pending_tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('check-developer-role/', check_developer_role, name='check_developer_role'),
    path('profile/', get_user_profile, name='get_user_profile'),
]

