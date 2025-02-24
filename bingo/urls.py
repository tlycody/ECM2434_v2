from django.shortcuts import render
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView

# Import views
from .views import (
    login_user, register_user, tasks, complete_task,
    leaderboard, get_user_profile, update_user_profile
)

# Function-based views
def home_page(request):
    return render(request, "home.html")

def bingo_home(request):
    return HttpResponse("Welcome to the Bingo API!")

# URL patterns
urlpatterns = [
    # Home routes
    path('', home_page, name='home'),
    path('bingo/', bingo_home, name='bingo_home'),

    # Authentication routes
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='api_login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # User profile
    path('user/', get_user_profile, name='get_user_profile'),
    path('user/update/', update_user_profile, name='update_user_profile'),

    # Game functionality
    path('tasks/', tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]
