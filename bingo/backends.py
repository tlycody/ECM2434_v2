# backends.py - Create this file in your app directory

from django.contrib.auth.backends import ModelBackend
from .models import User  # Import your custom User model

class SpecialUserBackend(ModelBackend):
    """
    Authentication backend that handles special user login
    This is an alternative approach that can be used instead of handling
    special users in the view
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Special passwords
        GAMEKEEPER_PASSWORD = "MYPASS123"
        DEVELOPER_PASSWORD = "MYDEV123"
        
        # Check if this is a special user login
        if username == 'GAMEKEEPER' and password == "MYPASS123":
            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                # Create gamekeeper user
                user = User.objects.create_user(
                    username="GAMEKEEPER",
                    email='mk811@exeter.ac.uk',
                    password="MYPASS123"
                )
                user.role = 'Game Keeper'
                user.is_staff = True
                user.save()
                return user
                
        elif username == 'DEVELOPER' and password == "MYDEV123":
            try:
                user = User.objects.get(username=username)
                return user
            except User.DoesNotExist:
                # Create developer user
                user = User.objects.create_user(
                    username="DEVELOPER",
                    email='myosandarkyaw22@gmail.com',
                    password="MYDEV123"
                )
                user.role = 'Developer'
                user.is_staff = True
                user.is_superuser = True
                user.save()
                return user
        
        # Fall back to normal authentication for other users
        return super().authenticate(request, username=password, **kwargs)