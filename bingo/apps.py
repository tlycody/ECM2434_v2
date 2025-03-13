# Import the base AppConfig class from Django's apps module
from django.apps import AppConfig
from django.db.models.signals import post_migrate


# Define a configuration class for the "bingo" app
class BingoConfig(AppConfig):
    # Set the default field type for auto-generated primary keys
    default_auto_field = "django.db.models.BigAutoField"
    
    # Define the name of the app as "bingo"
    name = "bingo"
    
    def ready(self):
        # Import signals when the app is ready
        import bingo.signals
        
        # Register the post_migrate signal to check database after migrations
        from django.db.models.signals import post_migrate
        post_migrate.connect(self.check_database, sender=self)
    
    def check_database(self, **kwargs):
        # This function will run after migrations are applied
        from .models import User, Leaderboard
        import os
        
        user_count = User.objects.count()
        leaderboard_count = Leaderboard.objects.count()
        
        print(f"===== DATABASE PERSISTENCE CHECK =====")
        print(f"Found {user_count} users in the database")
        print(f"Found {leaderboard_count} leaderboard entries")
        
        # Check the database file directly
        from django.conf import settings
        db_path = settings.DATABASES['default']['NAME']
        if os.path.exists(db_path):
            print(f"Database file exists at: {db_path}")
            print(f"Database file size: {os.path.getsize(db_path)} bytes")
        else:
            print(f"WARNING: Database file does not exist at: {db_path}")
        print(f"======================================")