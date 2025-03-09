# ============================
# Django View Functions for API Endpoints
# ============================

# Import Django utilities for authentication and file handling
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.urls import path
from django.core.files.storage import default_storage

# Import Django Rest Framework utilities
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Import models and serializers
from .models import Task, UserTask, Leaderboard, Profile, UserConsent
from .serializers import TaskSerializer, LeaderboardSerializer
from .views import get_user_profile, register_user

# Import other Python modules
import logging
import json
import os
from django.contrib.auth import get_user_model
User = get_user_model()

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Allowed image types for profile picture uploads
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]

# ============================
# Load Initial Tasks into Database
# ============================

def load_initial_tasks():
    """
    Loads initial tasks from 'initial_data.json' if no tasks exist in the database.
    """
    if not Task.objects.exists():
        try:
            json_file_path = os.path.join(os.path.dirname(__file__), 'initial_data.json')
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            for item in data:
                Task.objects.create(
                    id=item['pk'],
                    description=item['fields']['description'],
                    points=item['fields']['points'],
                    requires_upload=item['fields']['requires_upload'],
                    requires_scan=item['fields']['requires_scan']
                )
            print(" Auto-loaded initial_data.json into Task model.")
        except Exception as e:
            print(f" Failed to auto-load data: {str(e)}")

# ============================
# User Profile Update
# ============================

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Updates the user's profile details including username, email, and profile picture.
    """
    user = request.user
    data = request.data
    profile, created = Profile.objects.get_or_create(user=user)

    # Update username and email if provided
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    # Handle profile picture update
    if 'profile_picture' in request.FILES:
        file = request.FILES['profile_picture']

        # Validate file type
        if file.content_type not in ALLOWED_IMAGE_TYPES:
            return Response({"error": "Invalid file type. Only JPEG and PNG images are allowed."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Delete the existing profile picture before saving the new one
        if profile.profile_picture:
            profile.profile_picture.delete()

        profile.profile_picture = file

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})

# ============================
# User Registration
# ============================


# ============================
# User Login
# ============================

@api_view(['POST'])
def login_user(request):
    """
    Authenticates a user and returns JWT tokens.
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')

    # Validate input fields
    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': username
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

# ============================
# Task Retrieval
# ============================

@api_view(['GET'])
def tasks(request):
    """
    Retrieves all available tasks.
    """
    load_initial_tasks()  # Ensure initial tasks are loaded
    task_list = Task.objects.all()
    serializer = TaskSerializer(task_list, many=True)
    return JsonResponse(serializer.data, safe=False)

# ============================
# Task Completion
# ============================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request):
    """
    Marks a task as completed by the user and updates their leaderboard score.
    """
    user = request.user
    task_id = request.data.get('task_id')
    task = get_object_or_404(Task, id=task_id)

    # Check if task is already completed
    if UserTask.objects.filter(user=user, task=task).exists():
        return Response({"message": "Task already completed!"}, status=status.HTTP_400_BAD_REQUEST)

    # Mark task as completed
    UserTask.objects.create(user=user, task=task, completed=True)

    # Update leaderboard points
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.points += task.points
    leaderboard.save()

    return Response({"message": "Task completed!", "points": leaderboard.points})

# ============================
# Leaderboard Retrieval
# ============================

@api_view(['GET'])
def leaderboard(request):
    """
    Retrieves the top 10 players from the leaderboard.
    """
    top_players = Leaderboard.objects.order_by('-points')[:10]
    serializer = LeaderboardSerializer(top_players, many=True)
    return Response(serializer.data)

# ============================
# Check Developer Role
# ============================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_developer_role(request):
    """
    Checks if the authenticated user has a 'Developer' role.
    """
    if request.user.role == "Developer":
        return Response({"is_developer": True}, status=status.HTTP_200_OK)
    return Response({"is_developer": False}, status=status.HTTP_403_FORBIDDEN)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_tasks(request):
    """
    Shows all the pending tasks
    """
    if request.user.role not in ['GameKeeper']:
        return Response({"error":"Permission denied"}, status = status.HTTP_403_FORBIDDEN)
    
    pending = UserTask.objects.filter(completed = False)

    result = []
    for item in pending:
        result.append({
            'user_id': item.user.id,
            'username': item.user.username,
            'task_id': item.task.id,
            'task_description': item.task.description,
            'points': item.task.points,
        })

    return Response(result)

# ============================
# URL Patterns
# ============================

from django.urls import path

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('tasks/', tasks, name='tasks'),
    path('pending-tasks/', pending_tasks,name = 'pending-tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('check-developer-role/', check_developer_role, name='check_developer_role'),
    path('profile/', get_user_profile, name='get_user_profile'),
]
