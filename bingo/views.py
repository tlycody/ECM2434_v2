from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from django.core.files.storage import default_storage

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Task, UserTask, Leaderboard, Profile
from .serializers import TaskSerializer, LeaderboardSerializer
import logging
import json
import os
from django.core.management import call_command

User = get_user_model()
logger = logging.getLogger(__name__)
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png"]

def load_initial_tasks():
    """
    Loads initial tasks from initial_data.json if the Task model is empty.
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
            print("✅ Auto-loaded initial_data.json into Task model.")
        except Exception as e:
            print(f"❌ Failed to auto-load data: {str(e)}")

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
        file = request.FILES['profile_picture']

        if file.content_type not in ALLOWED_IMAGE_TYPES:
            return Response({"error": "Invalid file type. Only JPEG and PNG images are allowed."},
                            status=status.HTTP_400_BAD_REQUEST)

        if profile.profile_picture:
            profile.profile_picture.delete()

        profile.profile_picture = file

    user.save()
    profile.save()

    return Response({"message": "Profile updated successfully"})

@api_view(['POST'])
def register_user(request):
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password_again = data.get("passwordagain")
    email = data.get("email")
    gdprConsent = data.get("gdprConsent", False)
    if not gdprConsent:
        return Response("You must accept the Privacy Policy to register", status=status.HTTP_400_BAD_REQUEST)

    if not all([username, password, password_again, email]):
        return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

    if password != password_again:
        return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "This email is already registered."}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create_user(username=username, email=email, password=password)
    from .models import UserConsent
    UserConsent.objects.create(
        user=user,
        ip_address=request.META.get('REMOTE_ADDR')
    )
    Profile.objects.create(user=user)
    Leaderboard.objects.get_or_create(user=user)
    
    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    """
    Log in a user and return JWT tokens.
    """
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

@api_view(['GET'])
def tasks(request):
    load_initial_tasks()
    task_list = Task.objects.all()
    serializer = TaskSerializer(task_list, many=True)
    return JsonResponse(serializer.data, safe=False)

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

@api_view(['GET'])
def leaderboard(request):
    top_players = Leaderboard.objects.order_by('-points')[:10]
    serializer = LeaderboardSerializer(top_players, many=True)
    return Response(serializer.data)


# Remove this duplicated function with indentation issues
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_developer_role(request):
    """Check if the user has the Developer role"""
    user = request.user
    is_developer = user.role == 'Developer'
    
    return Response({
        'is_developer': is_developer,
        'username': user.username
    })