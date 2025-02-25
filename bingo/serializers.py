# Import necessary modules from Django REST framework
from rest_framework import serializers

# Import models from the application
from .models import Task, UserTask, Leaderboard, User

# Import Django settings and logging for debugging
from django.conf import settings
import logging

# Set up logging for debugging purposes
logger = logging.getLogger(__name__)

# ============================
# User Registration Serializer
# ============================

class RegisterUserSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, including custom validation
    and additional fields for password confirmation and user role selection.
    """
    passwordagain = serializers.CharField(write_only=True)  # Additional field for confirming password
    profile = serializers.ChoiceField(choices=User.ROLE_CHOICES, default='Player')  # User role selection

    class Meta:
        model = User  # Uses the custom User model
        fields = ['username', 'email', 'password', 'passwordagain', 'profile']
        extra_kwargs = {'password': {'write_only': True}}  # Password should not be readable in responses

    def validate_email(self, value):
        """
        Validate that the email is from the university domain (@exeter.ac.uk).
        """
        if not value.lower().endswith('@exeter.ac.uk'):
            raise serializers.ValidationError("Please use your @exeter.ac.uk email only.")
        return value.lower()

    def validate(self, data):
        """
        Ensure that both password fields match.
        """
        if data['password'] != data['passwordagain']:
            raise serializers.ValidationError({"passwordagain": "Passwords do not match"})
        return data

    def create(self, validated_data):
        """
        Create a new user instance, remove the password confirmation field,
        and initialize the user's leaderboard entry.
        """
        validated_data.pop('passwordagain')  # Remove redundant password field

        # Create the user with the provided credentials
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile=validated_data.get('profile', 'Player')  # Default role is "Player"
        )

        # Automatically create a leaderboard entry for the new user
        Leaderboard.objects.create(user=user)

        return user

# ============================
# Task Serializer
# ============================

class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer for the Task model, allowing API interactions with tasks.
    """
    class Meta:
        model = Task
        fields = ['id', 'description', 'points', 'requires_upload', 'requires_scan']

# ============================
# UserTask Serializer
# ============================

class UserTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for tracking users' progress on assigned tasks.
    """
    class Meta:
        model = UserTask
        fields = '__all__'  # Expose all fields in the API response

# ============================
# Leaderboard Serializer
# ============================

class LeaderboardSerializer(serializers.ModelSerializer):
    """
    Serializer for the Leaderboard model to display user rankings.
    """
    user = serializers.CharField(source='user.username')  # Display username instead of user ID

    class Meta:
        model = Leaderboard
        fields = ['user', 'points']  # Fields to be exposed in the leaderboard API response
