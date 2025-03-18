# Django View Functions for API Endpoints
import uuid

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
from .models import User
from django.utils.timezone import now

# Django Rest Framework Imports
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status


from .models import PasswordResetToken
from django.core.mail import send_mail
from django.conf import settings
from datetime import timedelta

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


DEBUG_PATTERN_CHECKING = False


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


    # Check if this is a delete request
    is_delete_request = data.get('delete_account') == True or data.get('is_deleted') == True
    
    if is_delete_request:
        # Handle profile deletion
        try:
            # Delete profile picture if it exists
            profile = Profile.objects.filter(user=user).first()
            if profile and profile.profile_picture:
                profile.profile_picture.delete()
            
            # Delete user tasks
            UserTask.objects.filter(user=user).delete()
            
            # Delete user badges
            UserBadge.objects.filter(user=user).delete()
            
            # Delete leaderboard entry
            Leaderboard.objects.filter(user=user).delete()
            
            # Delete profile
            Profile.objects.filter(user=user).delete()
            
            # Delete the user (this will cascade to delete related objects)
            user.delete()
            
            return Response({"message": "User account deleted successfully"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"Failed to delete user: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # If not deleting, proceed with normal update
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
    try:
        user = User.objects.create_user(username=username, email=email, password=password, role=role)
        UserConsent.objects.create(user=user, ip_address=request.META.get('REMOTE_ADDR'))
        Profile.objects.create(user=user)
        Leaderboard.objects.get_or_create(user=user)
        
        # Verify the user was created (this will show in your console/logs)
        print(f"✅ Created user {username} (ID: {user.id})")
        print(f"✅ Total users in database: {User.objects.count()}")
        
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        print(f"❌ Error creating user: {str(e)}")
        return Response({"error": f"Registration failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
    user = request.user
    task_id = request.data.get('task_id')
    task = get_object_or_404(Task, id=task_id)

    # Debug logging
    print(f"Processing task completion: task_id={task_id}, user={user.username}")
    print(f"Task details: description={task.description}, requires_scan={getattr(task, 'requires_scan', False)}")

    # Check if this task has scan functionality for auto-approval
    should_auto_approve = task.requires_scan if hasattr(task, 'requires_scan') else False

    # Check if task exists in user tasks
    user_task = UserTask.objects.filter(user=user, task=task).first()
    if user_task:
        print(f"Existing user_task found: status={user_task.status}, completed={user_task.completed}")

    # If task is already completed and approved, don't allow resubmission
    if user_task and user_task.completed:
        return Response({"message": "Task already completed and approved!"},
                        status=status.HTTP_400_BAD_REQUEST)

    # If task is pending approval, don't allow resubmission
    if user_task and user_task.status == 'pending' and not user_task.completed:
        return Response({"message": "Task already submitted and pending approval!"},
                        status=status.HTTP_400_BAD_REQUEST)

    # If photo is required but not provided
    if task.requires_upload and 'photo' not in request.FILES:
        return Response({"message": "This task requires a photo upload."},
                        status=status.HTTP_400_BAD_REQUEST)

    # If photo is provided, check for fraud
    if 'photo' in request.FILES:
        photo_file = request.FILES['photo']
        print(f"Photo provided: size={photo_file.size}, type={photo_file.content_type}")

        # Check file size
        if photo_file.size > 10 * 1024 * 1024:  # 10MB limit
            return Response({"message": "Photo is too large. Maximum size is 10MB."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Check file type
        if not photo_file.content_type.startswith('image/'):
            return Response({"message": "Uploaded file is not an image."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Perform fraud detection check before saving
        from .basic_image_fraud_detector import BasicImageFraudDetector

        try:
            # Read the image data
            photo_file.seek(0)  # Reset file pointer to beginning
            photo_data = photo_file.read()
            photo_file.seek(0)  # Reset file pointer again

            # Initialize the fraud detector
            detector = BasicImageFraudDetector(similarity_threshold=85)

            # Check if the image is fraudulent (similar to previously submitted images)
            is_fraudulent, similarity, matched_task_id = detector.is_image_fraudulent(
                photo_data,
                user_id=user.id  # Check against this user's submissions
            )

            print(
                f"Fraud detection results: is_fraudulent={is_fraudulent}, similarity={similarity:.2f}%, matched_task_id={matched_task_id}")

            # If fraudulent, reject the submission
            if is_fraudulent:
                matched_task = None
                if matched_task_id:
                    matched_task = UserTask.objects.filter(id=matched_task_id).first()

                matched_task_info = "unknown task"
                if matched_task:
                    matched_task_info = f"task '{matched_task.task.description}'"

                return Response({
                    "message": f"This image appears to be identical or very similar to a previously submitted image for {matched_task_info}.",
                    "similarity": f"{similarity:.1f}%",
                    "error": "Please take a new picture that clearly shows you completing this specific task."
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Log the error but continue - don't block submission if fraud detection fails
            print(f"Error during fraud detection: {str(e)}")
            logger.error(f"Error during fraud detection: {str(e)}")

    # If user_task exists but was rejected, update it
    if user_task and user_task.status == 'rejected':
        print("Updating previously rejected task")

        # If there was a photo, delete it before adding the new one
        if user_task.photo:
            user_task.photo.delete()

        # Update the existing task record
        user_task.status = 'approved' if should_auto_approve else 'pending'
        user_task.completed = should_auto_approve
        user_task.completion_date = timezone.now()
        user_task.rejection_reason = None  # Clear previous rejection reason

        # Save the new photo if provided
        if 'photo' in request.FILES:
            user_task.photo = request.FILES['photo']

        user_task.save()

        print(f"Updated task: status={user_task.status}, completed={user_task.completed}")

        # If the task is auto-approved, check for patterns and award points
        if should_auto_approve:
            # Award points
            try:
                profile = Profile.objects.get(user=user)
                profile.total_points += task.points
                profile.save()

                # Also update the leaderboard
                leaderboard, created = Leaderboard.objects.get_or_create(user=user)
                leaderboard.points += task.points
                leaderboard.save()

                print(f"Points awarded to {user.username}: {task.points}")

                # Check for patterns and award badges
                check_and_award_patterns(user)
            except Profile.DoesNotExist:
                print(f"Profile not found for user: {user.username}")
            except Exception as e:
                print(f"Error updating points: {str(e)}")

        message = "Task completed successfully!" if should_auto_approve else "Task resubmitted successfully and awaiting GameKeeper approval!"
        return Response({"message": message}, status=status.HTTP_200_OK)

    # Otherwise, create a new user task
    print("Creating new user task")
    new_user_task = UserTask(
        user=user,
        task=task,
        completed=should_auto_approve,
        status='approved' if should_auto_approve else 'pending'
    )

    # Save photo if provided
    if 'photo' in request.FILES:
        new_user_task.photo = request.FILES['photo']

    new_user_task.save()

    print(f"Created new task: status={new_user_task.status}, completed={new_user_task.completed}")

    # Award points and check patterns if auto-approved
    if should_auto_approve:
        try:
            profile = Profile.objects.get(user=user)
            profile.total_points += task.points
            profile.save()

            # Also update the leaderboard
            leaderboard, created = Leaderboard.objects.get_or_create(user=user)
            leaderboard.points += task.points
            leaderboard.save()

            print(f"Points awarded to {user.username}: {task.points}")

            # Check for patterns and award badges
            check_and_award_patterns(user)
        except Profile.DoesNotExist:
            print(f"Profile not found for user: {user.username}")
        except Exception as e:
            print(f"Error updating points: {str(e)}")

    message = "Task completed successfully!" if should_auto_approve else "Task submitted successfully and awaiting GameKeeper approval!"
    return Response({"message": message}, status=status.HTTP_200_OK)
# ============================
# Leaderboard Retrieval
# ============================


@api_view(['GET'])
def leaderboard_view(request):
    """Returns both lifetime and monthly leaderboard rankings with correct key names."""
    try:
        lifetime_leaderboard = list(Leaderboard.objects.order_by('-points')[:10].values('user__username', 'points'))
        monthly_leaderboard = list(Leaderboard.objects.order_by('-monthly_points')[:10].values('user__username', 'monthly_points'))

        # Rename "monthly_points" to "points" to match React expectations
        formatted_monthly_leaderboard = [
            {"user": entry["user__username"], "points": entry["monthly_points"]}
            for entry in monthly_leaderboard
        ]

        return JsonResponse({
            "lifetime_leaderboard": lifetime_leaderboard,
            "monthly_leaderboard": formatted_monthly_leaderboard,
        })
    except Exception as e:
        logger.error(f"Error fetching leaderboard data: {str(e)}")
        return JsonResponse({"error": "Failed to retrieve leaderboard data"}, status=500)







@api_view(['GET'])
def leaderboard(request):
    """Retrieves the top 10 players from the leaderboard ordered by highest points."""
    try:
        top_players = Leaderboard.objects.order_by('-points')[:10]
        serializer = LeaderboardSerializer(top_players, many=True)
        return Response(serializer.data)
    except Exception as e:
        logger.error(f"Error fetching top leaderboard players: {str(e)}")
        return Response({"error": "Failed to retrieve leaderboard"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




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
    Get the current user's profile information including task status and rejection reasons
    """
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)

    # Count completed tasks
    completed_tasks = UserTask.objects.filter(user=user, completed=True).count()

    # Get all user tasks for status display with rejection reasons
    user_tasks_list = UserTask.objects.filter(user=user)
    user_tasks_data = []
    for task in user_tasks_list:
        user_tasks_data.append({
            'task_id': task.task.id,
            'status': task.status,
            'completed': task.completed,
            'submission_date': task.completion_date,
            'rejection_reason': task.rejection_reason if task.status == 'rejected' else None
        })

    # First, check if new patterns have been completed but badges not awarded yet
    check_and_award_patterns(user)
    
    # Now get user badges (after possible updates from pattern detection)
    user_badges = UserBadge.objects.filter(user=user).select_related('pattern')
    badges_data = []
    for badge in user_badges:
        badges_data.append({
            'id': badge.pattern.id,
            'name': badge.pattern.name if badge.pattern.name else f"{badge.pattern.pattern_type} Pattern",
            'type': badge.pattern.pattern_type,
            'description': badge.pattern.description,
            'bonus_points': badge.pattern.bonus_points,
        })

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
        "rank": profile.rank,
        "user_tasks": user_tasks_data,
        "badges": badges_data  # Add badges to the response
    }

    return Response(profile_data)

def user_rank(points):
    """
    Determine user rank based on points
    """
    if points < 50:
        return "Beginner"
    elif points < 100:
        return "Intermediate"
    elif points >= 100:
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
    Stores approved image signatures for fraud detection.
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

    # Store image signatures for approved photos (for fraud detection)
    if user_task.photo and user_task.photo.name:
        try:
            from .basic_image_fraud_detector import BasicImageFraudDetector

            # Open and read the photo file
            user_task.photo.open('rb')
            photo_data = user_task.photo.read()
            user_task.photo.close()

            # Initialize fraud detector and save signatures
            detector = BasicImageFraudDetector()
            detector.save_image_signature(user_task.id, photo_data)

            logger.info(f"Saved image signature for task {user_task.id}")
        except Exception as e:
            # Log error but don't prevent approval
            logger.error(f"Error saving image signature: {str(e)}")

    # Mark as completed and update status
    user_task.completed = True
    user_task.status = 'approved'
    user_task.save()

    # Update leaderboard
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.points += task.points
    leaderboard.save()

    # Update profile total points
    profile, _ = Profile.objects.get_or_create(user=user)
    profile.total_points += task.points
    profile.save()

    # Debugging line
    print(f"Calling check_and_award_patterns for user {user.username}")

    # Call this function to check for and award patterns
    check_and_award_patterns(user)

    return Response({
        "message": f"Task approved for {user.username}. {task.points} points rewarded."
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reject_task(request):
    """
    Rejects a pending task submission.
    Only for GameKeepers and Developers.
    """
    if request.user.role.lower() not in ['gamekeeper', 'developer']:
        return Response({'error': "Permission denied"}, status=status.HTTP_403_FORBIDDEN)

    user_id = request.data.get('user_id')
    task_id = request.data.get('task_id')
    reason = request.data.get('reason', 'Task rejected by game keeper')

    user = get_object_or_404(User, id=user_id)
    task = get_object_or_404(Task, id=task_id)
    user_task = get_object_or_404(UserTask, user=user, task=task)

    if user_task.completed:
        return Response({"message": "Task already approved and cannot be rejected."},
                        status=status.HTTP_400_BAD_REQUEST)

    # Mark as rejected
    user_task.status = 'rejected'
    user_task.rejection_reason = reason
    user_task.save()

    return Response({
        "message": f"Task submission from {user.username} has been rejected."
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
    
    # First check if new patterns have been completed
    print(f"Checking for new patterns for user {user.username}")
    detected_patterns, new_patterns_found = check_and_award_patterns(user)
    
    if new_patterns_found:
        print(f"New patterns detected: {detected_patterns}")
    
    # Get all user badges
    user_badges = UserBadge.objects.filter(user=user).select_related('pattern')
    badges_data = []
    
    for badge in user_badges:
        badges_data.append({
            'id': badge.pattern.id,
            'name': badge.pattern.name,
            'type': badge.pattern.pattern_type,
            'description': badge.pattern.description,
            'bonus_points': badge.pattern.bonus_points,
        })
    
    return Response(badges_data)


def check_and_award_patterns(user):
    """Check if the user has completed any patterns and award badges and points"""
    try:
        # Only print header if debugging is enabled
        if DEBUG_PATTERN_CHECKING:
            print(f"\n\n==== CHECKING PATTERNS FOR USER: {user.username} ====")

        # Get all completed tasks for the user
        completed_tasks = UserTask.objects.filter(user=user, completed=True)

        if DEBUG_PATTERN_CHECKING:
            print(f"Found {completed_tasks.count()} completed tasks: {[t.task.id for t in completed_tasks]}")

            # DETAILED DEBUG: Print each completed task description
            for task in completed_tasks:
                print(f"  - Task {task.task.id}: {task.task.description}")

        # If no completed tasks, return early
        if not completed_tasks.exists():
            if DEBUG_PATTERN_CHECKING:
                print("No completed tasks found, skipping pattern check")
            return [], False

        # Get all tasks to understand grid positioning
        all_tasks = Task.objects.all().order_by('id')
        if DEBUG_PATTERN_CHECKING:
            print(f"Total tasks in system: {all_tasks.count()}")

        # Create grid representation
        grid = BingoPatternDetector.create_grid_from_tasks(completed_tasks, all_tasks, grid_size=3)

        if DEBUG_PATTERN_CHECKING:
            print(f"Grid representation:")
            for row in grid:
                print(f"  {row}")

        # Detect patterns with detailed logging
        detected_patterns = BingoPatternDetector.detect_patterns(grid, size=3)
        if DEBUG_PATTERN_CHECKING:
            print(f"Detected patterns: {detected_patterns}")

        # If no patterns detected, return early
        if not detected_patterns:
            if DEBUG_PATTERN_CHECKING:
                print("No patterns detected")
            return [], False

        # Get existing badges for user
        existing_badges = UserBadge.objects.filter(user=user).values_list('pattern__pattern_type', flat=True)
        if DEBUG_PATTERN_CHECKING:
            print(f"Existing badges: {list(existing_badges)}")

        # Get user's leaderboard entry
        leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
        if DEBUG_PATTERN_CHECKING:
            print(f"Current points: {leaderboard.points}")

        # Track if any new patterns were completed
        new_patterns_completed = False
        newly_added_patterns = []

        # Award new badges and points
        for pattern_type in detected_patterns:
            try:
                # Skip if user already has this badge
                if pattern_type in existing_badges:
                    if DEBUG_PATTERN_CHECKING:
                        print(f"User already has badge for pattern: {pattern_type}")
                    continue

                if DEBUG_PATTERN_CHECKING:
                    print(f"New pattern detected: {pattern_type}")
                newly_added_patterns.append(pattern_type)

                # Get the pattern details
                try:
                    # Get or create the pattern in the database
                    pattern, created = BingoPattern.objects.get_or_create(
                        pattern_type=pattern_type,
                        defaults={
                            'name': get_pattern_name(pattern_type),
                            'description': get_pattern_description(pattern_type),
                            'bonus_points': 30  # Default bonus points
                        }
                    )

                    if DEBUG_PATTERN_CHECKING:
                        if created:
                            print(f"Created new pattern in database: {pattern.name}")
                        else:
                            print(f"Found existing pattern in database: {pattern.name}")

                    # Create badge for user and award bonus points
                    UserBadge.objects.create(user=user, pattern=pattern)
                    if DEBUG_PATTERN_CHECKING:
                        print(f"Created UserBadge for pattern: {pattern.pattern_type}")

                    # Award pattern bonus points
                    leaderboard.points += pattern.bonus_points
                    if DEBUG_PATTERN_CHECKING:
                        print(f"Awarded {pattern.bonus_points} bonus points for pattern")

                    # Set flag to indicate a new pattern was completed
                    new_patterns_completed = True

                except Exception as e:
                    if DEBUG_PATTERN_CHECKING:
                        print(f"ERROR creating or retrieving pattern: {str(e)}")
            except Exception as inner_e:
                if DEBUG_PATTERN_CHECKING:
                    print(f"ERROR processing pattern {pattern_type}: {str(inner_e)}")

        if DEBUG_PATTERN_CHECKING:
            print(f"New patterns completed: {new_patterns_completed}")

        # Award additional points for completing a task that forms a bingo pattern
        if new_patterns_completed:
            if DEBUG_PATTERN_CHECKING:
                print("Awarding extra 5 points for pattern completion...")

            # Award extra points
            try:
                task_completion_bonus = 5
                leaderboard.points += task_completion_bonus
                leaderboard.save()
                if DEBUG_PATTERN_CHECKING:
                    print(f"Awarded {task_completion_bonus} extra points for pattern completion")

                # Create bonus record
                try:
                    # Get any completed task to link bonus to
                    some_task = completed_tasks.first()
                    if some_task:
                        TaskBonus.objects.create(
                            user=user,
                            task=some_task.task,
                            bonus_points=task_completion_bonus,
                            reason="Completed bingo pattern"
                        )
                        if DEBUG_PATTERN_CHECKING:
                            print(f"Created TaskBonus record")
                    else:
                        if DEBUG_PATTERN_CHECKING:
                            print("ERROR: No completed task found to link bonus to")
                except Exception as tb_error:
                    if DEBUG_PATTERN_CHECKING:
                        print(f"ERROR creating TaskBonus: {str(tb_error)}")
                    # Don't let TaskBonus creation failure prevent points from being awarded
                    pass
            except Exception as bonus_error:
                if DEBUG_PATTERN_CHECKING:
                    print(f"ERROR awarding extra points: {str(bonus_error)}")

        return newly_added_patterns, new_patterns_completed
    except Exception as e:
        if DEBUG_PATTERN_CHECKING:
            print(f"ERROR in check_and_award_patterns: {str(e)}")
        return [], False

# Helper functions for pattern names and descriptions
def get_pattern_name(pattern_type):
    """Return a friendly name for each pattern type"""
    pattern_names = {
        'O': 'Outer Circle Champion',
        'X': 'Diagonal Master',
        'H': 'Horizontal Hero',
        'V': 'Vertical Victory'
    }
    return pattern_names.get(pattern_type, f"{pattern_type} Pattern")

def get_pattern_description(pattern_type):
    """Return a description for each pattern type"""
    pattern_descriptions = {
        'O': 'Complete all tasks along the outer edge of the bingo board',
        'X': 'Complete tasks diagonally from corner to corner',
        'H': 'Complete all tasks in any horizontal row',
        'V': 'Complete all tasks in any vertical column'
    }
    return pattern_descriptions.get(pattern_type, f"Complete tasks in a {pattern_type} pattern")
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def force_award_pattern(request):
    """
    Manually force award a pattern to a user
    """ 
    # Use current user if no user_id provided
    user = request.user
    pattern_type = request.data.get('pattern_type', 'V')  # Default to vertical
    
    # Get or create the pattern
    pattern, created = BingoPattern.objects.get_or_create(
        pattern_type=pattern_type,
        defaults={
            'name': f"{pattern_type} Pattern",
            'description': f"Complete tasks in a {pattern_type} pattern",
            'bonus_points': 30
        }
    )
    
    # Check if user already has this badge
    if UserBadge.objects.filter(user=user, pattern=pattern).exists():
        return Response({"message": f"User already has the {pattern_type} badge"})
    
    # Award badge and points
    with transaction.atomic():
        # Create badge
        UserBadge.objects.create(user=user, pattern=pattern)
        
        # Get leaderboard
        leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
        old_points = leaderboard.points
        
        # Award pattern bonus
        leaderboard.points += pattern.bonus_points
        
        # Award extra completion bonus
        leaderboard.points += 5
        leaderboard.save()
        
        # Create bonus record if there are completed tasks
        some_task = UserTask.objects.filter(user=user, completed=True).first()
        if some_task:
            try:
                TaskBonus.objects.create(
                    user=user,
                    task=some_task.task,
                    bonus_points=5,
                    reason=f"Completed {pattern_type} pattern"
                )
            except Exception as e:
                print(f"Error creating TaskBonus: {str(e)}")
    
    return Response({
        "message": f"Awarded {pattern_type} badge and {pattern.bonus_points + 5} bonus points to {user.username}",
        "old_points": old_points,
        "new_points": leaderboard.points
    })
    
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('user_type', 'Player')  # Assuming 'user_type' from dropdown
        
        # Special passwords from your form
        GAMEKEEPER_PASSWORD = "MYPASS123"
        DEVELOPER_PASSWORD = "MYDEV123"
        
        # Special user handling
        special_user = False
        if role == 'GAMEKEEPER' and password == "MYPASS123":
            special_user = True
            # Check if user exists, create if not
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username="GAMEKEEPER",
                    email=f"mk811@exeter.ac.uk",
                    password="MYPASS123"
                )
                user.role = 'Game Keeper'
                user.is_staff = True
                user.save()
                
        elif role == 'DEVELOPER' and password == "MYDEV123":
            special_user = True
            # Check if user exists, create if not
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = User.objects.create_user(
                    username="DEVELOPER",
                    email=f"myosandarkyaw22@gmail.com",
                    password="MYDEV123"
                )
                user.role = 'Developer'
                user.is_staff = True
                user.is_superuser = True
                user.save()
        
        # Authenticate and login
        if special_user:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if role in ['Game Keeper', 'Developer']:
                    return redirect('/admin/')  # Redirect to admin
                return redirect('/')  # Or your game home
            else:
                messages.error(request, "Authentication failed")
        else:
            # Regular user authentication
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')  # Your main game page
            else:
                messages.error(request, "Invalid username or password")
    
    return render(request, 'login.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_tasks_status(request):
    """
    Retrieves the status of all tasks for the current user including rejection reasons.
    """
    user = request.user

    # Get all user tasks
    user_tasks = UserTask.objects.filter(user=user)

    # Format the response data
    tasks_status = []
    for user_task in user_tasks:
        tasks_status.append({
            'task_id': user_task.task.id,
            'status': user_task.status,
            'completed': user_task.completed,
            'submission_date': user_task.completion_date,
            'rejection_reason': user_task.rejection_reason if user_task.status == 'rejected' else None
        })

    return Response(tasks_status)


@api_view(['POST'])
def password_reset_request(request):
    email = request.data.get('email', '').lower().strip()

    if not email:
        return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

    # Find user by email
    user = User.objects.filter(email=email).first()

    if user:
        # Delete any existing unused tokens for this user
        PasswordResetToken.objects.filter(user=user, used=False).delete()

        # Create new token with 24-hour expiration
        expiry_time = timezone.now() + timedelta(hours=24)
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=expiry_time
        )

        # For development, use localhost URL
        frontend_url = 'http://localhost:3000'
        reset_url = f"{frontend_url}/reset-password/{reset_token.token}"

        # Debug print
        print("\n" + "="*50)
        print("PASSWORD RESET REQUESTED")
        print("="*50)
        print(f"User: {user.username}")
        print(f"Email: {email}")
        print(f"Token: {reset_token.token}")
        print(f"Reset URL: {reset_url}")
        print("="*50 + "\n")

        # Send email
        try:
            send_mail(
                'Password Reset Request',
                f'Click the link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            # Still return success to prevent user enumeration

    return Response({'message': 'If your email address is registered, you will receive a password reset link'})
@api_view(['POST'])
def password_reset_confirm(request):
    """
    Validates token and updates user password
    """
    token_string = request.data.get('token')
    new_password = request.data.get('password')

    if not token_string or not new_password:
        return Response({'error': 'Token and new password are required'},
                        status=status.HTTP_400_BAD_REQUEST)

    try:
        # Find the token
        reset_token = PasswordResetToken.objects.get(
            token=uuid.UUID(token_string),
            used=False,
            expires_at__gt=timezone.now()
        )

        # Validate password
        try:
            validate_password(new_password, reset_token.user)
        except ValidationError as e:
            return Response({'error': list(e.messages)}, status=status.HTTP_400_BAD_REQUEST)

        # Update password and mark token as used
        user = reset_token.user
        user.set_password(new_password)
        user.save()

        reset_token.used = True
        reset_token.save()

        return Response({'message': 'Password has been reset successfully'})

    except PasswordResetToken.DoesNotExist:
        return Response({'error': 'Invalid or expired token'},
                        status=status.HTTP_400_BAD_REQUEST)
    except ValueError:
        return Response({'error': 'Invalid token format'},
                        status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"Password reset error: {str(e)}")
        return Response({'error': 'An error occurred during password reset'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)