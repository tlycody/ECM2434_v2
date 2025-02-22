from rest_framework import serializers
from .models import Task, UserTask, Leaderboard
from django.contrib.auth.models import User
from django.db import models
from django.conf import settings
    
from rest_framework import serializers
from .models import User
import logging
logger = logging.getLogger(__name__)

class RegisterUserSerializer(serializers.ModelSerializer):
    passwordagain = serializers.CharField(write_only=True)
    profile = serializers.ChoiceField(choices=User.PROFILE_CHOICES, default='Player')

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'passwordagain', 'profile']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, value):
        if not value.lower().endswith('@exeter.ac.uk'):
            raise serializers.ValidationError("Please use your @exeter.ac.uk email only.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['passwordagain']:
            raise serializers.ValidationError({"passwordagain": "Passwords do not match"})
        return data

    def create(self, validated_data):
        validated_data.pop('passwordagain')
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile=validated_data.get('profile', 'Player')
        )
        
        # Create leaderboard entry
        Leaderboard.objects.create(user=user)
        
        return user
    
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = '__all__'

class UserTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTask
        fields = '__all__'

class LeaderboardSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Leaderboard
        fields = ['user', 'points']
