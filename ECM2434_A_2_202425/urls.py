from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('', include('bingo.urls')),  # Includes all API routes from the 'bingo' app
]

