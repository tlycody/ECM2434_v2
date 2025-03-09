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
from .views import force_award_pattern
from .views import get_user_profile, register_user, check_auth, approve_task, debug_user_tasks, debug_media_urls

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
    Ensures username and password validation.
    """
    data = request.data
    username = data.get('username')
    password = data.get('password')
    profile = data.get('profile')

    # Validate input fields
    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user:
        # Assign role based on the profile field
        if profile == "GameKeeper":
            user.role = "GameKeeper"  # Update the user's role
            user.save()  # Save the updated role to the database
            role = "GameKeeper"
        else:
            role = "Player"
        
        # Create a new token AFTER updating the role
        refresh = RefreshToken.for_user(user)
        
        # Add custom claims to the token payload
        refresh['role'] = user.role
        
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': username,
            'role': user.role  # Include the updated role in the response
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
    Submits a task for approval by the user.
    Task points are only awarded after GameKeeper approval.
    """
    user = request.user
    task_id = request.data.get('task_id')
    task = get_object_or_404(Task, id=task_id)

    # Check if task is already submitted or completed
    user_task = UserTask.objects.filter(user=user, task=task).first()
    if user_task:
        if user_task.completed:
            return Response({"message": "Task already completed and approved!"}, 
                          status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Task already submitted and pending approval!"}, 
                          status=status.HTTP_400_BAD_REQUEST)

    # Check if photo is required but not provided
    if task.requires_upload and 'photo' not in request.FILES:
        return Response({"message": "This task requires a photo upload."}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    # Create new user task - marked as not completed (pending approval)
    user_task = UserTask(user=user, task=task, completed=False)
    
    # Save photo if provided
    if 'photo' in request.FILES:
        user_task.photo = request.FILES['photo']
    
    user_task.save()

    return Response({"message": "Task submitted successfully and awaiting GameKeeper approval!"}, 
                  status=status.HTTP_200_OK)

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

# Update the pending_tasks function in views.py

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_tasks(request):
    """
    Shows all the pending tasks for GameKeepers to review
    """
    # Make the role check case-insensitive and include Developer role
    if request.user.role.lower() not in ['gamekeeper', 'developer']:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    # Filter tasks with status 'pending' or completed=False (for backward compatibility)
    pending = UserTask.objects.filter(status='pending', completed=False)
    
    # For debugging
    print(f"Found {pending.count()} pending tasks")
    
    result = []
    for item in pending:
        task_data = {
            'user_id': item.user.id,
            'username': item.user.username,
            'task_id': item.task.id,
            'task_description': item.task.description,
            'points': item.task.points,
            'requires_upload': item.task.requires_upload,
            'completion_date': item.completion_date,  # Changed from submission_date to completion_date
        }
        
        # Add photo URL if exists
        if item.photo:
            task_data['photo_url'] = request.build_absolute_uri(item.photo.url)
        
        result.append(task_data)

    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({
        "authenticated": True, 
        "username": request.user.username, 
        "role": request.user.role,
        "role_lowercase": request.user.role.lower() if request.user.role else None
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_user_tasks(request):
    """
    Debug endpoint to check all UserTask records and their statuses
    """
    if request.user.role.lower() not in ['gamekeeper', 'developer']:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all tasks
    all_tasks = UserTask.objects.all()
    
    result = {
        'total_tasks': all_tasks.count(),
        'pending_tasks': UserTask.objects.filter(status='pending', completed=False).count(),
        'completed_tasks': UserTask.objects.filter(completed=True).count(),
        'tasks_by_status': {
            'pending': UserTask.objects.filter(status='pending').count(),
            'approved': UserTask.objects.filter(status='approved').count(),
            'rejected': UserTask.objects.filter(status='rejected').count(),
        },
        'tasks_details': []
    }
    
    # Add details for each task
    for task in all_tasks:
        result['tasks_details'].append({
            'id': task.id,
            'user': task.user.username,
            'task_description': task.task.description,
            'status': task.status,
            'completed': task.completed,
            'has_photo': bool(task.photo),
            'completion_date': task.completion_date,
        })
    
    return Response(result)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_media_urls(request):
    """Debug endpoint to check media URLs and file existence"""
    if request.user.role.lower() not in ['gamekeeper', 'developer']:
        return Response({"error": "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    # Get all task photos
    pending_tasks = UserTask.objects.filter(completed=False)
    
    media_info = []
    for task in pending_tasks:
        task_info = {
            'task_id': task.id,
            'user': task.user.username,
            'has_photo_field': bool(task.photo),
            'photo_field_value': str(task.photo) if task.photo else None,
            'photo_url': None,
            'file_exists': False
        }
        
        if task.photo:
            # Get URL
            task_info['photo_url'] = request.build_absolute_uri(task.photo.url)
            
            # Check if file exists
            import os
            from django.conf import settings
            
            file_path = os.path.join(settings.MEDIA_ROOT, str(task.photo))
            task_info['file_exists'] = os.path.exists(file_path)
            task_info['file_path'] = file_path
        
        media_info.append(task_info)
    
    # Add server configuration for context
    config_info = {
        'MEDIA_URL': settings.MEDIA_URL,
        'MEDIA_ROOT': settings.MEDIA_ROOT,
        'DEBUG': settings.DEBUG,
        'BASE_DIR': str(settings.BASE_DIR)
    }
    
    return Response({
        'media_info': media_info,
        'config': config_info
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_task(request):
    """
    Approves a pending task submission.
    Only for GameKeepers and Developers.
    """
    if request.user.role.lower() not in ['gamekeeper', 'developer']:
        return Response({'error': "Permission denied"}, status=status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    task_id = request.data.get('task_id')  # Changed 'task' to 'task_id' for consistency

    user = get_object_or_404(User, id=user_id)
    task = get_object_or_404(Task, id=task_id)
    user_task = get_object_or_404(UserTask, user=user, task=task)

    if user_task.completed:
        return Response({"message": "Task already approved!"}, status=status.HTTP_400_BAD_REQUEST)
    
    # Mark as completed and update status
    user_task.completed = True
    user_task.status = 'approved'
    user_task.save()

    # Update leaderboard
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.points += task.points
    leaderboard.save()

    return Response({
        "message": f"Task approved for {user.username}. {task.points} points rewarded."
    })

# ============================
# URL Patterns
# ============================

from django.urls import path

urlpatterns = [
    path('register/', register_user, name='register_user'),
    path('login/', login_user, name='login_user'),
    path('check-auth/', check_auth, name='check_auth'),
    path('tasks/', tasks, name='tasks'),
    path('pending-tasks/', pending_tasks,name = 'pending-tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('approve-task/', approve_task, name='approve_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('profile/update/', update_user_profile, name='update_user_profile'),
    path('check-developer-role/', check_developer_role, name='check_developer_role'),
    path('profile/', get_user_profile, name='get_user_profile'),
    path('debug-tasks/', debug_user_tasks, name='debug_user_tasks'),
    path('debug-media/', debug_media_urls, name='debug_media_urls'),
    path('force-award-pattern/', force_award_pattern, name='force_award_pattern'),
]
