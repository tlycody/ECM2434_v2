from django.contrib import admin

# Register your models here.
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('api/', include('bingo.urls')),  # Includes all API routes from the 'bingo' app
]
