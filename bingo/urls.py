from django.urls import path
from bingo.views import login_user, get_user_profile, get_tasks, complete_task,leaderboard
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf.urls import include
from django.conf import settings
from .views import RegisterUserView

urlpatterns = [
    path('register_user/', RegisterUserView.as_view(), name='register'),
    path('login/', login_user, name='login'),
    path('user/', get_user_profile, name='user'),
    path('api/token/refresh/', TokenRefreshView.as_view(),name ='token_refresh'),
    path('tasks/', get_tasks, name='tasks'),
    path('complete_task/', complete_task, name='complete_task'),
    path('leaderboard/', leaderboard, name='leaderboard'),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [path('__debug__/', include(debug_toolbar.urls))]