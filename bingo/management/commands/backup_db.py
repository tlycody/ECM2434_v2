from django.core.management.base import BaseCommand
import os
import shutil
import time
from django.conf import settings

class Command(BaseCommand):
    help = 'Backup the SQLite database'
    
    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f"Database file not found at {db_path}"))
            return
        
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(settings.BASE_DIR, 'db_backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Create backup with timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"db_backup_{timestamp}.sqlite3")
        
        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f"Database backed up successfully to {backup_path}"))
            
            # Also create a "latest" backup that will be included in Git
            latest_backup = os.path.join(settings.BASE_DIR, 'db_latest_backup.sqlite3')
            shutil.copy2(db_path, latest_backup)
            self.stdout.write(self.style.SUCCESS(f"Created latest backup at {latest_backup}"))
            
            # Show database stats
            db_size = os.path.getsize(db_path)
            self.stdout.write(f"Database size: {db_size} bytes")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error backing up database: {str(e)}"))