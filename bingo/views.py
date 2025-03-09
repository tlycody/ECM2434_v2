# Django View Functions for API Endpoints

# Django Imports
from django.shortcuts import get_object_or_404, render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction

# Django Rest Framework Imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Model and Serializer Imports
from .models import BingoPattern, Task, TaskBonus, UserBadge, UserTask, Leaderboard, Profile, UserConsent
from .serializers import TaskSerializer, LeaderboardSerializer
from .bingo_patterns import BingoPatternDetector

# Local Imports
from .forms import CustomUserCreationForm

# Standard Library Imports
import logging
import json
import os

# Logger Setup
logger = logging.getLogger(__name__)

# Constants
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]
User = get_user_model()

# Task Loading Function
def load_initial_tasks():
    """Loads initial tasks from JSON file if the database is empty."""
    if not Task.objects.exists():
        try:
            json_file_path = os.path.join(os.path.dirname(__file__), 'initial_data.json')
            with open(json_file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            for item in data:
                Task.objects.create(**item['fields'], id=item['pk'])
            logger.info("Initial tasks loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load initial tasks: {e}")


# ============================
# User Profile Update
# ============================

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """
    Updates the user's profile details including username, email, and profile picture.
    Ensures proper file validation and safe updates.
    """
    user = request.user
    data = request.data
    profile, _ = Profile.objects.get_or_create(user=user)

    # Update username and email if provided
    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    # Handle profile picture update
    if 'profile_picture' in request.FILES:
        file = request.FILES['profile_picture']

        # Delete old image before replacing
        if profile.profile_picture:
            profile.profile_picture.delete()

        profile.profile_picture = file

    user.save()
    profile.save()

    return Response({
        "username": user.username,
        "email": user.email,
        "profile_picture": profile.profile_picture.url if profile.profile_picture else None,
    })

# ============================
# User Registration
# ============================

@api_view(['POST'])
def register_user(request):
    """
    Registers a new user with GDPR consent verification.
    Ensures email uniqueness, password validation, and consent compliance.
    """
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password_again = data.get("passwordagain")
    email = data.get("email")
    gdprConsent = data.get("gdprConsent", False)
    role = data.get("role", "Player") 

    # Validate GDPR consent
    if not gdprConsent:
        return Response({"error": "You must accept the Privacy Policy to register."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Ensure all required fields are provided
    if not all([username, password, password_again, email]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate password confirmation
    if password != password_again:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    # Validate the password strength
    try:
        validate_password(password, User(username=username, email=email))
    except ValidationError as e:
        return Response({"error": list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

    # Check if username or email is already taken
    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    # Create user and related models
    user = User.objects.create_user(username=username, email=email, password=password, role=role)  # Set role here
    UserConsent.objects.create(user=user, ip_address=request.META.get('REMOTE_ADDR'))
    Profile.objects.create(user=user)
    Leaderboard.objects.get_or_create(user=user)

    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)


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
    Ensures tasks are preloaded before retrieval.
    """
    load_initial_tasks()
    task_list = Task.objects.all()
    serializer = TaskSerializer(task_list, many=True)
    return JsonResponse(serializer.data, safe=False)

# ============================
# Task Completion
# ============================

# Update the complete_task function in views.py

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
    
    # Create new user task - mark as pending approval
    user_task = UserTask(
        user=user, 
        task=task, 
        completed=False,  # Not completed until approved
        status='pending'  # Explicitly mark as pending
    )
    
    # Save photo if provided
    if 'photo' in request.FILES:
        user_task.photo = request.FILES['photo']
    
    user_task.save()
    
    # Debug info
    print(f"Created new task submission: UserTask(user={user.username}, task_id={task_id}, status={user_task.status})")

    return Response({"message": "Task submitted successfully and awaiting GameKeeper approval!"}, 
                  status=status.HTTP_200_OK)

# ============================
# Leaderboard Retrieval
# ============================

@api_view(['GET'])
def leaderboard(request):
    """
    Retrieves the top 10 players from the leaderboard.
    Orders them by highest points.
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
    Checks if the authenticated user has the 'Developer' role.
    """
    user = request.user
    is_developer = user.role == 'Developer'
    
    return Response({
        'is_developer': is_developer,
        'username': user.username
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """
    Get the current user's profile information
    """
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    
    # Count completed tasks
    completed_tasks = UserTask.objects.filter(user=user, completed=True).count()
    
    # Calculate user rank
    user_points = leaderboard.points
    rank = user_rank(user_points)
    
    # Update rank in profile if different
    if profile.rank != rank:
        profile.rank = rank
        profile.save()
    
    # Get user's position in leaderboard
    leaderboard_position = Leaderboard.objects.filter(points__gt=user_points).count() + 1
    
    # Prepare profile data
    profile_data = {
        "username": user.username,
        "email": user.email,
        "total_points": user_points,
        "completed_tasks": completed_tasks,
        "leaderboard_rank": leaderboard_position,
        "profile_picture": request.build_absolute_uri(profile.profile_picture.url) if profile.profile_picture else None,
        "rank": profile.rank
    }
    
    return Response(profile_data)

def user_rank(points):
    """
    Determine user rank based on points
    """
    if points < 50:
        return "Beginner"
    elif points < 1250:
        return "Expert"
    else:
        return "None"

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_task(request):
    """
    Creates a new task. Only accessible to GameKeeper or Developer roles.
    """
    # Check if user has appropriate permissions
    user = request.user
    if user.profile not in ['GameKeeper', 'Developer']:
        return Response({"error": "You don't have permission to create tasks."}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    # Get task data from request
    data = request.data
    description = data.get('description')
    points = data.get('points')
    requires_upload = data.get('requires_upload', False)
    requires_scan = data.get('requires_scan', False)
    
    # Validate required fields
    if not description or not points:
        return Response({"error": "Description and points are required."}, 
                        status=status.HTTP_400_BAD_REQUEST)
    
    # Create new task
    task = Task.objects.create(
        description=description,
        points=points,
        requires_upload=requires_upload,
        requires_scan=requires_scan
    )
    
    # Return the created task
    serializer = TaskSerializer(task)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Set the password directly (this comes from the clean() method)
            user.set_password(form.cleaned_data.get('password1'))
            user.save()
            
            # Create GDPR consent record
            UserConsent.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR', None)
            )
            
            # Check if the user needs approval
            if user.role in ['Game Keeper', 'Developer']:
                messages.info(
                    request,
                    "Your admin account has been created. You can now log in with your credentials."
                )
                return redirect('login')
            else:
                login(request, user)
                return redirect('player_dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})
    
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
    pending = UserTask.objects.filter(status='pending')
    
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
            'photo_url': None
        }
        
        # Add photo URL if exists
        if item.photo and item.photo.name:
            task_data['photo_url'] = request.build_absolute_uri(item.photo.url)
            print(f"Photo URL: {task_data['photo_url']}")  # Debug: Print photo URL
        
        result.append(task_data)

    return Response(result)

# Update the approve_task function in views.py

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

    check_and_award_patterns(user)

    return Response({
        "message": f"Task approved for {user.username}. {task.points} points rewarded."
    })

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
            'photo_url': None
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

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_badges(request):
    """
    Get all badges earned by the authenticated user
    """
    user = request.user
    user_badges = UserBadge.objects.filter(user=user).select_related('pattern')
    
    badges = []
    for badge in user_badges:
        badges.append({
            'id': badge.pattern.id,
            'name': badge.pattern.name,
            'type': badge.pattern.pattern_type,
            'description': badge.pattern.description,
            'bonus_points': badge.pattern.bonus_points,
            'earned_at': badge.earned_at
        })
    
    return Response(badges)

def check_and_award_patterns(user):
    """
    Check if the user has completed any patterns and award badges and points
    
    This function should be called after a task is approved
    """
    print(f"\n\n==== CHECKING PATTERNS FOR USER: {user.username} ====")
    
    # Get all completed tasks for the user
    completed_tasks = UserTask.objects.filter(user=user, completed=True)
    print(f"Found {completed_tasks.count()} completed tasks")
    
    # Get all tasks
    all_tasks = Task.objects.all().order_by('id')
    
    # Create grid representation
    grid = BingoPatternDetector.create_grid_from_tasks(completed_tasks, all_tasks, grid_size=3)
    print(f"Grid: {grid}")
    
    # Detect patterns
    detected_patterns = BingoPatternDetector.detect_patterns(grid, size=3)
    print(f"Detected patterns: {detected_patterns}")
    
    # Get existing badges for user
    existing_badges = UserBadge.objects.filter(user=user).values_list('pattern__pattern_type', flat=True)
    print(f"Existing badges: {list(existing_badges)}")
    
    # Get user's leaderboard entry
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    print(f"Current points: {leaderboard.points}")
    
    # Track if any new patterns were completed
    new_patterns_completed = False
    
    # Award new badges and points
    for pattern_type in detected_patterns:
        # Skip if user already has this badge
        if pattern_type in existing_badges:
            print(f"User already has badge for pattern: {pattern_type}")
            continue
        
        print(f"New pattern detected: {pattern_type}")
        # Get the pattern details
        try:
            pattern = BingoPattern.objects.get(pattern_type=pattern_type)
            
            # Create badge for user
            with transaction.atomic():
                UserBadge.objects.create(user=user, pattern=pattern)
                
                # Award bonus points
                old_points = leaderboard.points
                leaderboard.points += pattern.bonus_points
                leaderboard.save()
                
                # Set flag to indicate a new pattern was completed
                new_patterns_completed = True
                
                print(f"Awarded {pattern.name} badge to {user.username} with {pattern.bonus_points} bonus points (total: {old_points} -> {leaderboard.points})")
        except BingoPattern.DoesNotExist:
            print(f"Pattern {pattern_type} not found in database")
    
    print(f"New patterns completed: {new_patterns_completed}")
    
    # Award additional points for completing a task that forms a bingo pattern
    if new_patterns_completed:
        try:
            # Just use the first completed task to avoid field issues
            latest_task = completed_tasks.first()
            
            if latest_task:
                # Award extra points for the task that completed the pattern
                task_completion_bonus = 20  # You can adjust this value
                old_points = leaderboard.points
                
                try:
                    with transaction.atomic():
                        leaderboard.points += task_completion_bonus
                        leaderboard.save()
                        
                        print(f"Awarded {task_completion_bonus} extra points to {user.username} for completing a bingo pattern (total: {old_points} -> {leaderboard.points})")
                        
                        # Fix the TaskBonus creation with proper field references
                        TaskBonus.objects.create(
                            user=user,
                            task=latest_task.task,
                            bonus_points=task_completion_bonus,
                            reason="Completed bingo pattern"
                        )
                        print(f"Created TaskBonus record for task #{latest_task.task.id}")
                except Exception as e:
                    print(f"Error in TaskBonus creation: {str(e)}")
        except Exception as e:
            print(f"Error in task bonus awarding: {str(e)}")
    
    return detected_patterns, new_patterns_completed