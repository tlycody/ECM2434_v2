from django.contrib import admin
from .models import Challenge, UserChallenge,  Reward

# Register your models here.
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Django Admin Panel
    path('api/', include('bingo.urls')),  # Includes all API routes from the 'bingo' app
]

admin.site.register(Challenge)
admin.site.register(UserChallenge)
admin.site.register(Reward)