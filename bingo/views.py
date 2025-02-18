from django.shortcuts import render

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task, UserTask, Leaderboard, BingoTask
from .serializers import TaskSerializer, UserTaskSerializer, LeaderboardSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

@api_view(['POST'])
def login_user(request):
    """Authenticates a user and returns JWT tokens"""
    data = request.data
    user = authenticate(username=data['username'], password=data['password'])

    if user is not None:
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def register_user(request):
    """Registers a new user"""
    data = request.data

    if User.objects.filter(username=data['username']).exists():
        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.create(
        username=data['username'],
        password=make_password(data['password'])  # Hash the password
    )

    return Response({"message": "User registered successfully"}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_tasks(request):
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

    user_task = UserTask.objects.create(user=user, task=task, completed=True)

    leaderboard, created = Leaderboard.objects.get_or_create(user=user)
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
    completed_tasks = BingoTask.objects.filter(completed_by=user).count()
    total_points = sum(task.points for task in BingoTask.objects.filter(completed_by=user))

    return Response({
        "username": user.username,
        "total_points": total_points,
        "completed_tasks": completed_tasks
    })

