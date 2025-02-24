from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    PROFILE_CHOICES = [
        ('Player', 'Player'),
        ('Game Keeper', 'Game Keeper'),
        ('Developer', 'Developer'),
    ]
    profile = models.CharField(
        max_length=20,
        choices=PROFILE_CHOICES,
        default='Player',
        blank=True,  # Make the field optional
        null=True    # Allow NULL in the database
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    

class Task(models.Model):
    description = models.TextField()
    points = models.IntegerField()
    requires_upload = models.BooleanField(default=False)
    requires_scan = models.BooleanField(default=False)

    def __str__(self):
        return self.description


class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.description}"


class Leaderboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} Points"
