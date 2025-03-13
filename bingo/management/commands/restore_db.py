from django.core.management.base import BaseCommand
import os
import shutil
from django.conf import settings

class Command(BaseCommand):
    help = 'Restore the SQLite database from backup'
    
    def handle(self, *args, **options):
        db_path = settings.DATABASES['default']['NAME']
        backup_path = os.path.join(settings.BASE_DIR, 'db_latest_backup.sqlite3')
        
        if not os.path.exists(backup_path):
            self.stdout.write(self.style.ERROR(f"Backup file not found at {backup_path}"))
            return
        
        try:
            # Create a backup of current DB if it exists
            if os.path.exists(db_path):
                temp_backup = f"{db_path}.bak"
                shutil.copy2(db_path, temp_backup)
                self.stdout.write(f"Created temporary backup at {temp_backup}")
            
            # Restore from backup
            shutil.copy2(backup_path, db_path)
            os.chmod(db_path, 0o664)  # Set proper permissions
            
            self.stdout.write(self.style.SUCCESS(f"Database restored successfully from {backup_path}"))
            self.stdout.write(f"Restored database size: {os.path.getsize(db_path)} bytes")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error restoring database: {str(e)}"))