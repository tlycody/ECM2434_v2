from django.urls import path
from .views import register_user, login_user, get_user_profile, get_tasks, complete_task,leaderboard
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register_user/', register_user, name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_profile, name='user'),
    path('api/token/refresh/', TokenRefreshView.as_view(),name ='token_refresh'),
    path('tasks/', get_tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
