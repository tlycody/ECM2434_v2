from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task, UserTask, Leaderboard, Profile
from .serializers import TaskSerializer, LeaderboardSerializer
from rest_framework_simplejwt.tokens import RefreshToken
import logging
from rest_framework.parsers import MultiPartParser, FormParser

User = get_user_model()
logger = logging.getLogger(__name__)


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Profile
from django.core.files.storage import default_storage

User = get_user_model()

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_profile(request):
    """Update user profile details including profile picture"""
    user = request.user
    data = request.data
    profile, created = Profile.objects.get_or_create(user=user)

    user.username = data.get('username', user.username)
    user.email = data.get('email', user.email)

    if 'profile_picture' in request.FILES:
        if profile.profile_picture:
            default_storage.delete(profile.profile_picture.path)  # Delete old file
        profile.profile_picture = request.FILES['profile_picture']

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})


# ✅ Validate email domain (Exeter only)
def email_validation(email):
    try:
        validate_email(email)
        return email.lower().endswith('@exeter.ac.uk')
    except ValidationError:
        return False

def get_client_ip(request):
    forward = request.META.get('HTTP_X_FORWARDED_FOR')
    if forward:
        ip = forward.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

# ✅ Register new user (with error handling)
@api_view(['POST'])
def register_user(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password_again = data.get("passwordagain")
    email = data.get("email")
    gdprConsent = data.get("gdprConsent",False)
    if not gdprConsent:
        return Response("You must accept the Privacy Policy to register",status=status.HTTP_400_BAD_REQUEST)

    if not all([username, password, password_again, email]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if password != password_again:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    if not email_validation(email):
        return Response({"error": "Please use your @exeter.ac.uk email only."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    from .models import UserConsent
    UserConsent.objects.create(
        user = user,
        ip_address = get_client_ip(request)
    )
    Profile.objects.create(user=user)
    Leaderboard.objects.get_or_create(user=user)
    
    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

# ✅ Login user & return JWT token
@api_view(['POST'])
def login_user(request):
    data = request.data
    username = data.get('username')
    password = data.get('password')

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

# ✅ Fetch all tasks (public API)
@api_view(['GET'])
def tasks(request):
    task_list = Task.objects.all()
    serializer = TaskSerializer(task_list, many=True)
    return Response(serializer.data)

# ✅ Mark a task as completed & update leaderboard
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def complete_task(request):
    user = request.user
    task_id = request.data.get('task_id')
    task = get_object_or_404(Task, id=task_id)

    if UserTask.objects.filter(user=user, task=task).exists():
        return Response({"message": "Task already completed!"}, status=status.HTTP_400_BAD_REQUEST)

    UserTask.objects.create(user=user, task=task, completed=True)
    leaderboard, _ = Leaderboard.objects.get_or_create(user=user)
    leaderboard.points += task.points
    leaderboard.save()

    return Response({"message": "Task completed!", "points": leaderboard.points})

# ✅ Retrieve the leaderboard (top 10)
@api_view(['GET'])
def leaderboard(request):
    top_players = Leaderboard.objects.order_by('-points')[:10]
    serializer = LeaderboardSerializer(top_players, many=True)
    return Response(serializer.data)

# ✅ Get individual user profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    completed_tasks = UserTask.objects.filter(user=user, completed=True).count()
    leaderboard_entry = Leaderboard.objects.filter(user=user).first()
    total_points = leaderboard_entry.points if leaderboard_entry else 0
    profile = Profile.objects.filter(user=user).first()

    return Response({
        "username": user.username,
        "email": user.email,
        "total_points": total_points,
        "completed_tasks": completed_tasks,
        "leaderboard_rank": user_rank(total_points),
        "profile_picture": profile.profile_picture.url if profile and profile.profile_picture else None
    })

# ✅ Determine user rank based on points
def user_rank(points):
    if points < 50:
        return "Beginner"
    elif points > 1250:
        return "Expert"
    return "Intermediate"
