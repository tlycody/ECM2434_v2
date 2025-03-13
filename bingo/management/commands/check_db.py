from django.core.management.base import BaseCommand
import os
from django.conf import settings

class Command(BaseCommand):
    help = 'Check database existence and persistence'
    
    def handle(self, *args, **options):
        # Check database file
        db_path = settings.DATABASES['default']['NAME']
        self.stdout.write(f"Checking database at: {db_path}")
        
        if os.path.exists(db_path):
            self.stdout.write(self.style.SUCCESS(f"✅ Database file exists ({os.path.getsize(db_path)} bytes)"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Database file not found! Will be created."))
            
        # Check user data
        try:
            from bingo.models import User
            user_count = User.objects.count()
            self.stdout.write(self.style.SUCCESS(f"✅ Connected to database. Found {user_count} users."))
            
            if user_count > 0:
                self.stdout.write("Sample users:")
                for user in User.objects.all()[:5]:
                    self.stdout.write(f"  • {user.username}")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error checking users: {e}"))