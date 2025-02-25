from .models import Task, UserTask, Leaderboard,User, Profile, UserConsent
from django.contrib import admin
from django.urls import path, include

# Register your models with the admin site
admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(Leaderboard)
admin.site.register(Profile)
admin.site.register(UserConsent)
