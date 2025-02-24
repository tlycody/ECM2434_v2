from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.core.files.storage import default_storage
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import Task, UserTask, Leaderboard, BingoTask
from .serializers import TaskSerializer, LeaderboardSerializer
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import logging
import os
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from django.contrib.auth import get_user_model

from bingo import models

User = get_user_model()

logger = logging.getLogger(__name__)

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
    logger.info(f"Incoming Registration request:{data}")
    username = data.get('username')
    password = data.get('password')
    profile=data.get('profile') 
    extra_password = data.get('extraPassword','')

    def log_error(error_message, status_code):
        logger.error(f"Registration error: {error_message}")
        return Response({"detail": error_message}, status_code)

    #To check the user exists
    user_exists = User.objects.filter(username=username).exists()
    logger.info(f"User exists:{user_exists}")


    """To make sure there is a validate input"""
    if not data.get("username") or not data.get("password"):
        return Response({"error": "You need to fill out both username and password."}, status=status.HTTP_400_BAD_REQUEST)
    
    valid_profiles = ['Player', 'Game Keeper', 'Developer']
    if profile not in valid_profiles:
        return Response({"error": "Invalid profile."}, status=status.HTTP_400_BAD_REQUEST)

    """To check the user exists"""
    if not User.objects.filter(username=username).exists():
        logger.warning(f"Login attempt for non-existent user: {username}")
        return Response(
            {"error": "Invalid username or password"}, 
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    """This is to authenticate the user"""
    user = authenticate(username=username, password=password)
    logger.info(f"Authentication result for user {username}: {'success' if user else 'failed'}")

    if user is not None:  
      GK_PASSWORD = os.environ.get('GK_PASSWORD','GKFeb2025BINGO#')
      DV_PASSWORD = os.environ.get('DV_PASSWORD','DVFeb2025BINGO@')

      if profile == 'Game Keeper' and extra_password != GK_PASSWORD:
        return log_error("Invalid special password.",status.HTTP_400_BAD_REQUEST)
       
      if profile == 'Developer' and extra_password != DV_PASSWORD:
        return log_error("Invalid special password.",status.HTTP_400_BAD_REQUEST)
    
      refresh = RefreshToken.for_user(user)
      return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user':username
        }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def register_user(request):
    """Registers a new user"""
    data = request.data
    username = data.get("username")
    password = data.get("password")
    password_again = data.get("passwordagain")
    email = request.data.get("email")
    logger.info(f"Incoming registration request: {data}")

    def log_error(error_message, status_code):
        logger.error(f"Registration error: {error_message}")
        return Response({"detail": error_message}, status_code)

    """To make sure there is a validate input"""

    if not data.get("username") or not data.get("password"):
        return log_error("Both username and password are required.", status.HTTP_400_BAD_REQUEST)
    
    if not email:
        return log_error("Email is required. ",status.HTTP_400_BAD_REQUEST)
    
    if not email_validation(email):
        return log_error("Please use your @exeter.ac.uk email only.",status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=data['username']).exists():
        return log_error("Username already taken", status.HTTP_400_BAD_REQUEST)
    
    if User.objects.filter(email=email).exists():
        return log_error("This email has already registered.", status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(data.get('password'))
    except ValidationError as e:
        return log_error("This password is weak. Make a stronger one.",status.HTTP_400_BAD_REQUEST)

    if data.get('password') != data.get('passwordagain'):
        error_message = "Passwords do not match."
        logger.error(error_message)
        return log_error(error_message,status.HTTP_400_BAD_REQUEST)
    
    try:
        user = create_user(data, email)
        return Response({"message": "User registered successfully!"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return log_error(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

def create_user(data, email):
    try:
        logger.info(f"Creating user account for {data['username']}")
        user = User.objects.create_user(
            username=data['username'],
            email=email,
            password=data['password'],
        )
        # Create leaderboard entry
        try:
            Leaderboard.objects.get_or_create(user=user)
            logger.info(f"Leaderboard entry created for {user.username}")
        except Exception as e:
            # If leaderboard creation fails, delete the user and raise error
            user.delete()
            logger.error(f"Failed to create leaderboard for {user.username}: {str(e)}")
            raise

        logger.info(f"User account created successfully for {user.username}")
        return user
    except Exception as e:
        logger.error(f"Failed to create user account: {str(e)}")
        raise

@api_view(['GET'])
def check_user(request,username):
    user = User.objects.filter(username = username).first()
    if user:
        return Response({
            'exists': True,
            'email':user.email
        })
    return Response({'exists': False, 'error': 'User not found'})

@api_view(['GET'])
def tasks(request):
    tasks_list =     [{
      'id': 1,
      'description': "Finish Green Consultant training",
      'points': 10,
      'requiresUpload': True,
      "requireScan": False,
    },
    {
      'id': 2,
      'description':  "Join a 'Green' society",
      'points': 7,
      'requiresUpload': True,
      "requireScan": False,
    },
    {
      'id': 3,
      'description':  "Get involved in Gift it, Reuse it scheme",
      'points': 10,
      'requiresUpload': False,
      "requireScan": True,
    },
    {
      'id': 4,
      'description': "Use British Heart Foundation Banks on campus to recycle clothes",
      'points': 8,
      'requiresUpload':False,
       "requireScan": True,
    },
    {
      'id': 5,
      'description': "Sign up to university sustainability newsletter",
      'points': 5,
      'requiresUpload': True,
      "requireScan": False,
    },
    {
      'id': 6,
      'description': "Refill your reusable water bottle from one of over 100 free water refill stations on campus",
      'points': 8,
      'requiresUpload': True,
       "requireScan": False,
    },
    {
      'id': 7,
      'description': "Shopping at Exeter's zero waste shops, Nourish and Zero",
      'points': 10,
      'requiresUpload': False,
      "requireScan": True,
    },
    {
      'id': 8,
      'description': "Empty glasses put in nearest glass bottle bank",
      'points': 8,
      'requiresUpload': True,
       "requireScan": False,
    },
    {
      'id': 9,
      'description': "Getting involved in ESV - Environmental Project",
      'points': 10,
      'requiresUpload':False,
       "requireScan": True,
    }]
    return JsonResponse(tasks_list, safe=False) 

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
        