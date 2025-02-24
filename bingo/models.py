from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

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

class Challenge(models.Model):
    TASK_TYPES = (
        ('location', 'Location-based'),
        ('photo', 'Photo Upload'),
    )
    
    PATTERN_TYPES = [
        ('row', 'Row'),
        ('column', 'Column'),
        ('diagonal', 'Diagonal')
    ]
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    task_type = models.CharField(max_length=10, choices=TASK_TYPES)
    points = models.IntegerField(default=10)
    qr_code = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_part_of_pattern = models.BooleanField(default=False)
    pattern_type = models.CharField(max_length=20, choices=PATTERN_TYPES, null=True, blank=True)

    def __str__(self):
        return self.name
    
    class UserChallenge(models.Model):
      user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
      challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE)
      completed = models.BooleanField(default=False)
      completed_at = models.DateTimeField(null=True, blank=True)
      photo = models.ImageField(upload_to='challenge_photos/', blank=True, null=True)

    def complete_challenge(self):
        self.completed = True
        self.completed_at = now()
        self.save()

    def calculate_time_bonus(self):
        if not self.completed:
            return 0
        weeks_diff = (now() - self.challenge.created_at).days // 7
        if weeks_diff == 0:
            return 40
        elif weeks_diff == 1:
            return 30
        elif weeks_diff == 2:
            return 20
        elif weeks_diff == 3:
            return 10
        return 0

    def get_total_points(self):
        base_points = self.challenge.points if self.completed else 0
        time_bonus = self.calculate_time_bonus()
        return base_points + time_bonus

    def __str__(self):
        return f"{self.user.username} - {self.challenge.name}"
    
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