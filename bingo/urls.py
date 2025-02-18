from django.urls import path
from .views import get_tasks, complete_task, leaderboard

urlpatterns = [
    path('tasks/', get_tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
