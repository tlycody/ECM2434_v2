from django.core.management.base import BaseCommand
from bingo.models import User, Leaderboard

class Command(BaseCommand):
    help = 'Check database persistence and user data'
    
    def handle(self, *args, **options):
        user_count = User.objects.count()
        self.stdout.write(f"Found {user_count} users in the database")
        
        if user_count > 0:
            self.stdout.write("Sample users:")
            for user in User.objects.all()[:5]:  # Show first 5 users
                self.stdout.write(f"- {user.username} (ID: {user.id}, Email: {user.email})")
        
        leaderboard_count = Leaderboard.objects.count()
        self.stdout.write(f"Found {leaderboard_count} leaderboard entries")
        
        if user_count == 0:
            create_test = input("No users found. Create a test user? (y/n): ")
            if create_test.lower() == 'y':
                user = User.objects.create_user(
                    username='testpersistence',
                    email='test@example.com',
                    password='TestPassword123'
                )
                Leaderboard.objects.create(user=user, points=100)
                self.stdout.write(self.style.SUCCESS(f"Created test user 'testpersistence' with password 'TestPassword123'"))