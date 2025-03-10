from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates special users (gamekeeper and developer) for admin access'

    def handle(self, *args, **options):
        # Special passwords from your form
        GAMEKEEPER_PASSWORD = "MYPASS123"
        DEVELOPER_PASSWORD = "MYDEV123"
        
        # Get current timestamp for unique emails
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        
        # Create gamekeeper user
        try:
            if User.objects.filter(username='GAMEKEEPER').exists():
                gamekeeper = User.objects.get(username='GAMEKEEPER')
                gamekeeper.set_password("MYPASS123")
                # Only update role and permissions, don't change email
                if hasattr(gamekeeper, 'role'):
                    gamekeeper.role = 'Game Keeper'
                gamekeeper.is_staff = True
                gamekeeper.save()
                self.stdout.write(self.style.SUCCESS('Updated gamekeeper user'))
            else:
                # Try with your preferred email first, but have fallback for conflicts
                try:
                    gamekeeper = User.objects.create_user(
                        username='GAMEKEEPER',
                        email='mk811@exeter.ac.uk',
                        password="MYPASS123"
                    )
                except IntegrityError:
                    # If email conflict, use a unique email
                    gamekeeper = User.objects.create_user(
                        username='GAMEKEEPER',
                        email=f'gamekeeper_{timestamp}@example.com',
                        password="MYPASS123"
                    )
                    
                if hasattr(gamekeeper, 'role'):
                    gamekeeper.role = 'Game Keeper'
                gamekeeper.is_staff = True
                gamekeeper.save()
                self.stdout.write(self.style.SUCCESS('Created new gamekeeper user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error with gamekeeper user: {e}'))

        # Create developer user
        try:
            if User.objects.filter(username='DEVELOPER').exists():
                developer = User.objects.get(username='DEVELOPER')
                developer.set_password("MYDEV123")
                # Only update role and permissions, don't change email
                if hasattr(developer, 'role'):
                    developer.role = 'Developer'
                developer.is_staff = True
                developer.is_superuser = True
                developer.save()
                self.stdout.write(self.style.SUCCESS('Updated developer user'))
            else:
                # Try with your preferred email first, but have fallback for conflicts
                try:
                    developer = User.objects.create_user(
                        username='DEVELOPER',
                        email='myosandarkyaw22@gmail.com',
                        password="MYDEV123"
                    )
                except IntegrityError:
                    # If email conflict, use a unique email
                    developer = User.objects.create_user(
                        username='DEVELOPER',
                        email=f'myosandarkyaw22@gmail.com',
                        password="MYDEV123"
                    )
                    
                if hasattr(developer, 'role'):
                    developer.role = 'Developer'
                developer.is_staff = True
                developer.is_superuser = True
                developer.save()
                self.stdout.write(self.style.SUCCESS('Created new developer user'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error with developer user: {e}'))