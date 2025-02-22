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
        default='Player'
    )

    def __str__(self):
        return self.username

class BingoTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField(default=10)
    completed_by = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_location_based = models.BooleanField(default=False)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    photo_required = models.BooleanField(default=False)
    points = models.IntegerField(default=5)

class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)