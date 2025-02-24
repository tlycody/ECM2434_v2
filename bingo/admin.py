from .models import Task, UserTask, Leaderboard
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('api/', include('bingo.urls')),  # Includes all API routes from the 'bingo' app
]

admin.site.register(Task)
admin.site.register(UserTask)
admin.site.register(Leaderboard)
