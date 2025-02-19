from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
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

def email_validation(email):
    """To validate, this is particularly for University of Exeter"""
    try:
        validate_email(email)
        if not email.lower().endswith('@exeter.ac.uk'):
           return False
        return True
    except ValidationError:
        return False
        
@api_view(['POST'])
def login_user(request):
    """Authenticates a user and returns JWT tokens"""
    data = request.data

    """To make sure there is a validate input"""
    if not data.get("username") or not data.get("password"):
        return Response({"error": "You need to fill out both username and password."}, status=status.HTTP_400_BAD_REQUEST)

    """This is to authenticate the user"""
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

    """To make sure there is a validate input"""

    if not data.get('username'):
        return Response({"error": "Username is required. "},status=status.HTTP_400_BAD_REQUEST)

    if not data.get("username") or not data.get("password"):
        return Response({"error": "Both username and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    email = data.get('email','').strip()
    if not email:
        return Response({"error": "Email is required. "},status=status.HTTP_400_BAD_REQUEST)
    
    if not validate_email(email):
        return Response({"error": "Please use your @exeter.ac.uk email only."},status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=data['username']).exists():
        return Response({"error": "Username already taken"}, status=status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return Response({"error": "This email has already registered."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(data.get('password'))
    except ValidationError as e:
        return Response({"error": "This password is weak. Make a stronger one."},status=status.HTTP_400_BAD_REQUEST)

    if data.get('password') != data.get('passwordagain'):
        return Response({"error": "Passwords do not match."},status=status.HTTP_400_BAD_REQUEST)
    
    #user account 
    try:
        user = User.objects.create(
        username=data['username'],
        email = email,
        password=make_password(data['password'])  
    )
        #user_leaderboard_entry
        Leaderboard.objects.create(user=user)

        refresh = RefreshToken.for_user(user) 
        return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'user': user.username,
        'email': user.email,
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SEVER_ERROR)
    
    #user_Leaderboard_entry


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
    total_points = leaderboard.points

    return Response({
        "username": user.username,
        "total_points": total_points,
        "completed_tasks": completed_tasks,
        "leaderboard-rank": user_rank(total_points)
    })

def user_rank(points):
    if points < 50:
        return "Beginner"
    elif points > 1250:
        return "Expert"
    else:
        return None 
        