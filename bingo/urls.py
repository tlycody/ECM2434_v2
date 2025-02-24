from django.shortcuts import render
from django.urls import path
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from .views import (
    login_user, register_user,
    #player_dashboard, gamekeeper_dashboard, developer_dashboard,
    tasks, complete_task, leaderboard
)
from rest_framework_simplejwt.views import TokenRefreshView

def home_page(request):
    return render(request, "home.html")

# New home view for the bingo app
def bingo_home(request):
    return HttpResponse("Welcome to the Bingo API!")
urlpatterns = [
    path('', home_page, name='home'),
    path('api/register/', register_user, name='register'),
    path('api/login/', login_user, name='api_login'),  # New route
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('player/', player_dashboard, name='player_dashboard'),
    # path('gamekeeper/', gamekeeper_dashboard, name='gamekeeper_dashboard'),
    # path('developer/', developer_dashboard, name='developer_dashboard'),   
    # Game functionality
    path('tasks/', tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
    path('register/', register_user, name='register_user'),
    path('get_user_profile/', get_user_profile, name='get_user_profile'),

]

