# ============================
# Django View Functions for API Endpoints
# ============================

# Import necessary Django modules
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login

# Import Django Rest Framework utilities
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

# Import models and serializers
from .models import Task, UserTask, Leaderboard, Profile, UserConsent
from .serializers import TaskSerializer, LeaderboardSerializer

#local application imports
from .forms import CustomUserCreationForm
# Import Python modules
import logging
import json
import os

# Set up logging for debugging
logger = logging.getLogger(__name__)

# Allowed image types for profile picture uploads
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]

# Get custom user model
User = get_user_model()

# ============================
# Load Initial Tasks into Database
# ============================

def load_initial_tasks():
    """
    Loads initial tasks from 'initial_data.json' if no tasks exist in the database.
    Ensures the game has predefined tasks available.
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
            logger.info("✅ Auto-loaded initial_data.json into Task model.")
        except Exception as e:
            logger.error(f"❌ Failed to auto-load data: {str(e)}")

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
    user = User.objects.create_user(username=username, email=email, password=password)
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
    Ensures tasks are preloaded before retrieval.
    """
    load_initial_tasks()
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
    Prevents duplicate completions.
    """
    user = request.user
    task_id = request.data.get('task_id')
    task = get_object_or_404(Task, id=task_id)

    # Check if task is already completed
    user_task = UserTask.objects.filter(user=user, task=task).first()
    if user_task:
        if user_task.completed:
            return Response({"message": "Task already completed!"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"message": "Task already submitted and pending approval!"}, 
                          status=status.HTTP_400_BAD_REQUEST)

    # Check if photo is required but not provided
    if task.requires_upload and 'photo' not in request.FILES:
        return Response({"message": "This task requires a photo upload."}, 
                      status=status.HTTP_400_BAD_REQUEST)
    
    # Create new user task
    user_task = UserTask(user=user, task=task, completed=False)
    
    # Save photo if provided
    if 'photo' in request.FILES:
        user_task.photo = request.FILES['photo']
    
    user_task.save()

    return Response({"message": "Task submitted for approval!"}, status=status.HTTP_200_OK)

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
    elif points < 1251:
        return "Intermediate"
    else:
        return "Expert"

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
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pending_tasks(request):
    """
    Shows all the pending tasks
    """
    print(f"User role: {request.user.role}")  # Debug print
    if request.user.role not in ['GameKeeper']:
        return Response({"error":"Permission denied"}, status = status.HTTP_403_FORBIDDEN)
    
    pending = UserTask.objects.filter(completed = False)

    result = []
    for item in pending:
        task_data =({
            'user_id': item.user.id,
            'username': item.user.username,
            'task_id': item.task.id,
            'task_description': item.task.description,
            'points': item.task.points,
            'requires_upload': item.task.requires_upload,
            'submission_date': item.submission_date,
        })
            # Add photo URL if exists
        if item.photo:
            task_data['photo_url'] = request.build_absolute_uri(item.photo.url)
        
        result.append(task_data)

    return Response(result)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def approve_task(request):
    """
    Approves a pending task submission.
    Only for GameKeepers and Developers.
    """
    if request.user.role not in ['GameKeeper']:
        return Response({'error': "Permission denied"}, status = status.HTTP_403_FORBIDDEN)
    
    user_id = request.data.get('user_id')
    task_id = request.data.get('task')

    user = get_object_or_404(User, id = user_id)
    task = get_object_or_404(Task, id = task_id)
    user_task = get_object_or_404(UserTask,user=user,task=task)

    if user_task.completed:
        return Response({"message": "Tasks already approved!"}, status = status.HTTP_400_BAD_REQUEST)
    
    user_task.completed = True
    user_task.save()

    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.points += task.points
    leaderboard.save()

    return Response({"message": f"Task approved for {user.username}.{task.points} points rewarded."})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth(request):
    return Response({"authenticated": True, "username": request.user.username, "role": request.user.role})