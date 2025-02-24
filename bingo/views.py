from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task, UserTask, Leaderboard
from .serializers import TaskSerializer, LeaderboardSerializer
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import os

User = get_user_model()
logger = logging.getLogger(__name__)

def email_validation(email):
    """Validate University of Exeter email"""
    try:
        validate_email(email)
        return email.lower().endswith('@exeter.ac.uk')
    except ValidationError:
        return False

@api_view(['POST'])
def register_user(request):
    """Registers a new user"""
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password_again = data.get("passwordagain")
    email = data.get("email")

    if not username or not password or not password_again or not email:
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
    Leaderboard.objects.get_or_create(user=user)
    return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)

@api_view(['POST'])
def login_user(request):
    """Authenticate a user and return JWT tokens"""
    data = request.data
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return Response({"error": "Username and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=username, password=password)
    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': username
        }, status=status.HTTP_200_OK)
    return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
def tasks(request):
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)

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
    players = Leaderboard.objects.order_by('-points')[:10]
    serializer = LeaderboardSerializer(players, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    completed_tasks = UserTask.objects.filter(user=user, completed=True).count()
    total_points = Leaderboard.objects.filter(user=user).first().points if Leaderboard.objects.filter(user=user).exists() else 0

    return Response({
        "username": user.username,
        "total_points": total_points,
        "completed_tasks": completed_tasks,
        "leaderboard_rank": user_rank(total_points)
    })

def user_rank(points):
    if points < 50:
        return "Beginner"
    elif points > 1250:
        return "Expert"
    return "Intermediate"