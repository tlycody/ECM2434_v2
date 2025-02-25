# Import necessary models from the models module
from .models import Task, UserTask, Leaderboard, User, Profile, UserConsent

# Import Django's admin module to register models for the admin interface
from django.contrib import admin
from django.urls import path, include  # Not used in this file but commonly needed for URL routing

# Register models with the Django admin site to manage them through the admin panel
admin.site.register(Task)  # Task model for managing tasks
admin.site.register(UserTask)  # Tracks task assignments and completions by users
admin.site.register(Leaderboard)  # Stores leaderboard data for gamification
admin.site.register(Profile)  # Extends the default User model with additional details
admin.site.register(UserConsent)  # Manages user consent data for compliance and permissions
