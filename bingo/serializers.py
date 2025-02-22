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
    profile = serializers.CharField()
    extraPassword = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'passwordagain', 'profile', 'extraPassword']

    def validate_email(self, value):
        if not value.lower().endswith('@exeter.ac.uk'):
            raise serializers.ValidationError("Please use your @exeter.ac.uk email only.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['passwordagain']:
            raise serializers.ValidationError({"passwordagain": "Passwords do not match"})
        
        profile = data.get('profile')
        extra_password = data.get('extraPassword', '')
        
        if profile in ['Game Keeper', 'Developer']:
            if not extra_password:
                raise serializers.ValidationError({"extraPassword": "Special password required for this profile"})
            
            if profile == 'Game Keeper' and extra_password != 'GKFeb2025BINGO#':
                raise serializers.ValidationError({"extraPassword": "Invalid special password"})
            elif profile == 'Developer' and extra_password != 'DVFeb2025BINGO@':
                raise serializers.ValidationError({"extraPassword": "Invalid special password"})
        
        return data

    def create(self, validated_data):
        # Remove extra fields that aren't part of the User model
        validated_data.pop('passwordagain')
        extra_password = validated_data.pop('extraPassword', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile=validated_data['profile']
        )
        
        # Create leaderboard entry
        from .models import Leaderboard
        Leaderboard.objects.create(user=user)
        
        return user

    def validate_email(self, value):
        if not value.lower().endswith('@exeter.ac.uk'):
            raise serializers.ValidationError("Please use your @exeter.ac.uk email only.")
        return value.lower()

    def validate(self, data):
        if data['password'] != data['passwordagain']:
            raise serializers.ValidationError({"passwordagain": "Passwords do not match"})
        
        profile = data.get('profile')
        extra_password = data.get('extraPassword', '')
        
        if profile in ['Game Keeper', 'Developer']:
            if not extra_password:
                raise serializers.ValidationError({"extraPassword": "Special password required for this profile"})
            
            if profile == 'Game Keeper' and extra_password != 'GKFeb2025BINGO#':
                raise serializers.ValidationError({"extraPassword": "Invalid special password"})
            elif profile == 'Developer' and extra_password != 'DVFeb2025BINGO@':
                raise serializers.ValidationError({"extraPassword": "Invalid special password"})
        
        return data

    def create(self, validated_data):
        validated_data.pop('passwordagain')
        validated_data.pop('extraPassword', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile=validated_data['profile']
        )
        
        # Create leaderboard entry
        from .models import Leaderboard
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
