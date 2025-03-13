from django.core.management.base import BaseCommand
from bingo.models import User, Leaderboard, Profile, UserConsent

class Command(BaseCommand):
    help = 'Initialize database with test users'
    
    def handle(self, *args, **options):
        # Check if users already exist
        if User.objects.exists():
            self.stdout.write(self.style.WARNING("Users already exist in database. Use --force to override."))
            if options.get('force'):
                self.stdout.write("Forcing recreation of test users...")
            else:
                return
        
        # Create test users
        users = [
            {'username': 'player1', 'email': 'player1@example.com', 'password': 'TestPassword123', 'role': 'Player'},
            {'username': 'player2', 'email': 'player2@example.com', 'password': 'TestPassword123', 'role': 'Player'},
            {'username': 'gamekeeper', 'email': 'gamekeeper@example.com', 'password': 'TestPassword123', 'role': 'GameKeeper'}
        ]
        
        for user_data in users:
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
                
                self.stdout.write(self.style.SUCCESS(f"Created user: {user_data['username']}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error creating {user_data['username']}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Created {len(users)} test users"))

    def add_arguments(self, parser):
        parser.add_argument('--force', action='store_true', help='Force recreation of test users')