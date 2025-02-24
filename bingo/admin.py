from django.contrib import admin
from django.urls import path, include
from django.contrib import admin
from .models import UserTask

admin.site.register(UserTask)

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('api/', include('bingo.urls')),  # Includes all API routes from the 'bingo' app
]
