from django.urls import path
from .views import register_user, login_user, get_user_profile, get_tasks, complete_task, leaderboard

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_profile, name='user'),
    path('tasks/', get_tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
