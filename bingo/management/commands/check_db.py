from django.core.management.base import BaseCommand
from bingo.models import User, Leaderboard, Profile, UserConsent
from django.db import transaction
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Initialize database with test users while preserving existing data'
    
    def handle(self, *args, **options):
        # Get database path
        db_path = settings.DATABASES['default']['NAME']
        db_exists = os.path.exists(db_path)
        db_size = os.path.getsize(db_path) if db_exists else 0
        
        self.stdout.write(f"Database path: {db_path}")
        self.stdout.write(f"Database exists: {db_exists}")
        self.stdout.write(f"Database size: {db_size} bytes")
        
        # Check current users
        existing_users = User.objects.all()
        user_count = existing_users.count()
        self.stdout.write(f"Found {user_count} existing users")
        
        if user_count > 0:
            self.stdout.write(self.style.SUCCESS("Database already has users. Preserving existing data."))
            # List existing users
            self.stdout.write("Existing users:")
            for user in existing_users[:5]:  # Show up to 5 users
                self.stdout.write(f"- {user.username} (Email: {user.email}, Role: {user.role})")
            
            if not options.get('force'):
                return
        
        # Default test users to add if none exist
        test_users = [
            {'username': 'player1', 'email': 'player1@example.com', 'password': 'Password123!', 'role': 'Player'},
            {'username': 'player2', 'email': 'player2@example.com', 'password': 'Password123!', 'role': 'Player'},
            {'username': 'gamekeeper', 'email': 'gamekeeper@example.com', 'password': 'Password123!', 'role': 'GameKeeper'}
        ]
        
        # Only add users if they don't already exist
        with transaction.atomic():
            users_added = 0
            for user_data in test_users:
                if not User.objects.filter(username=user_data['username']).exists():
                    try:
                        # Create user
                        user = User.objects.create_user(
                            username=user_data['username'],
                            email=user_data['email'],
                            password=user_data['password'],
                            role=user_data['role']
                        )
                        
                        # Create related models
                        Profile.objects.create(user=user)
                        UserConsent.objects.create(user=user, ip_address='127.0.0.1')
                        Leaderboard.objects.create(user=user, points=100 if user_data['role'] == 'Player' else 0)
                        
                        users_added += 1
                        self.stdout.write(self.style.SUCCESS(f"Created user: {user_data['username']}"))
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f"Error creating {user_data['username']}: {str(e)}"))
            
            if users_added > 0:
                self.stdout.write(self.style.SUCCESS(f"Added {users_added} new test users"))
            else:
                self.stdout.write("No new users were added")

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force addition of test users even if users exist')