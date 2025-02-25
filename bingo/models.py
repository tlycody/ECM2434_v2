# Import necessary Django modules for database models
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# ============================
# Custom User Model
# ============================

class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds a role field to categorize users into different roles.
    """
    ROLE_CHOICES = [
        ('Player', 'Player'),  # Regular players in the game
        ('Game Keeper', 'Game Keeper'),  # Moderators who verify game tasks
        ('Developer', 'Developer'),  # Developers with admin privileges
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Player',
        blank=True,
        null=True
    )

    email = models.EmailField(unique=True)  # Ensures each user has a unique email

    def __str__(self):
        """Returns the username as the string representation of the user."""
        return self.username

# ============================
# User Consent Model
# ============================

class UserConsent(models.Model):
    """
    Model to store GDPR consent information for each user.
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name="gdprConsent"
    )  # Links consent record to a user

    consented_at = models.DateTimeField(auto_now_add=True)  # Timestamp of consent
    ip_address = models.GenericIPAddressField(null=True, blank=True)  # Stores IP address for legal compliance

    def __str__(self):
        """Returns a formatted string representation of consent details."""
        return f"{self.user.username} - Consent on {self.consented_at}"

# ============================
# Profile Model
# ============================

class Profile(models.Model):
    """
    User profile model containing additional details such as profile pictures,
    ranking, and total points.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name="profile"
    )  # Links the profile to a user

    profile_picture = models.ImageField(
        upload_to='profile_pics/', 
        null=True, 
        blank=True
    )  # Allows users to upload a profile picture

    rank = models.CharField(max_length=50, default="Unranked")  # Stores the user's rank in the game
    total_points = models.IntegerField(default=0)  # Stores total points earned by the user

    def __str__(self):
        """Returns the username as the string representation of the profile."""
        return self.user.username

# ============================
# Task Model
# ============================

class Task(models.Model):
    """
    Model representing tasks that players must complete.
    Each task has a description, point value, and conditions for completion.
    """
    description = models.TextField()  # Stores the task description
    points = models.IntegerField()  # The number of points the task is worth
    requires_upload = models.BooleanField(default=False)  # Whether a photo upload is required
    requires_scan = models.BooleanField(default=False)  # Whether scanning a QR code is required

    def __str__(self):
        """Returns the task description as its string representation."""
        return self.description

# ============================
# UserTask Model
# ============================

class UserTask(models.Model):
    """
    Model representing a user's progress on specific tasks.
    Tracks task completion and stores proof (photo) if required.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )  # Links the task completion to a specific user

    task = models.ForeignKey(
        Task, 
        on_delete=models.CASCADE
    )  # Links the task completion to a specific task

    completed = models.BooleanField(default=False)  # Whether the user has completed the task
    photo = models.ImageField(
        upload_to='uploads/', 
        blank=True, 
        null=True
    )  # Stores a photo if required for verification

    completion_date = models.DateTimeField(auto_now_add=True)  # Timestamp of task completion

    def __str__(self):
        """Returns a formatted string of the user and task completed."""
        return f"{self.user.username} - {self.task.description}"

# ============================
# Leaderboard Model
# ============================

class Leaderboard(models.Model):
    """
    Model to track and rank players based on points earned.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )  # Links leaderboard entry to a user

    points = models.IntegerField(default=0)  # Stores the total points for ranking

    def __str__(self):
        """Returns a formatted string showing the user's leaderboard ranking."""
        return f"{self.user.username} - {self.points} Points"
