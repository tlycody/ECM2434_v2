from django.urls import path
from django.http import HttpResponse
from .views import login_user, get_user_profile, complete_task, leaderboard, RegisterUserView, TasksView
from rest_framework_simplejwt.views import TokenRefreshView

# New home view for the bingo app
def bingo_home(request):
    return HttpResponse("Welcome to the Bingo API!")

urlpatterns = [
    path('', bingo_home, name='bingo_home'),  # ✅ This ensures /bingo/ works
    path('register_user/', RegisterUserView.as_view(), name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_profile, name='user'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/tasks/', TasksView.as_view(), name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
