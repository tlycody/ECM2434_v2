from django.db import models
from django.contrib.auth.models import User


class BingoTask(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    points = models.IntegerField(default=10)
    completed_by = models.ManyToManyField(User, blank=True)

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    photo = models.ImageField(upload_to='uploads/', blank=True, null=True)
    completion_date = models.DateTimeField(auto_now_add=True)

class Leaderboard(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    points = models.IntegerField(default=0)