from django.urls import path
from django.http import HttpResponse
from django.contrib.auth import views as auth_views
from .views import (
    login_user, RegisterUserView, home_view,
    player_dashboard, gamekeeper_dashboard, developer_dashboard,
    tasks, complete_task, leaderboard
)
from rest_framework_simplejwt.views import TokenRefreshView

# New home view for the bingo app
def bingo_home(request):
    return HttpResponse("Welcome to the Bingo API!")
urlpatterns = [
    path('', home_view, name='home'),
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', login_user, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    
    # Dashboard URLs
    path('player/', player_dashboard, name='player_dashboard'),
    path('gamekeeper/', gamekeeper_dashboard, name='gamekeeper_dashboard'),
    path('developer/', developer_dashboard, name='developer_dashboard'),
    
    # Game functionality
    path('tasks/', tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]

