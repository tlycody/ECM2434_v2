from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser

# Custom User Model
class User(AbstractUser):
    ROLE_CHOICES = [
        ('Player', 'Player'),
        ('Game Keeper', 'Game Keeper'),
        ('Developer', 'Developer'),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='Player',
        blank=True,
        null=True
    )
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.username
    
class UserConsent(models.Model):
    user = models.OneToOneField(User,on_delete = models.CASCADE,related_name = "gdprConsent")
    consented_at = models.DateTimeField(auto_now_add = True)
    ip_address = models.GenericIPAddressField(null= True,blank=True)

    def __str__(self):
        return f"{self.user.username} -Consent on {self.consented_at}"


from django.conf import settings
from django.db import models

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    rank = models.CharField(max_length=50, default="Unranked")
    total_points = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username



# Task Model
class Task(models.Model):
    description = models.TextField()
    points = models.IntegerField()
    requires_upload = models.BooleanField(default=False)
    requires_scan = models.BooleanField(default=False) 

    def __str__(self):
        return self.description


# UserTask Model
class UserTask(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.task.description}"


# Leaderboard Model
class Leaderboard(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.user.username} - {self.points} Points"
