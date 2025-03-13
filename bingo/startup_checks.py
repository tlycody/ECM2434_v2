import os
import logging

logger = logging.getLogger(__name__)

def check_database_persistence():
    """
    Check if the database exists and has user data at startup.
    """
    from django.conf import settings
    from bingo.models import User, Leaderboard
    
    db_path = settings.DATABASES['default']['NAME']
    
    # Check if database file exists
    if not os.path.exists(db_path):
        logger.warning(f"Database file not found at {db_path}! A new one will be created.")
        return
    
    # Check database size
    db_size = os.path.getsize(db_path)
    logger.info(f"Database file size: {db_size} bytes")
    
    # Check for user data
    try:
        user_count = User.objects.count()
        leaderboard_count = Leaderboard.objects.count()
        logger.info(f"Found {user_count} users and {leaderboard_count} leaderboard entries")
        
        if user_count == 0:
            logger.warning("No users found in the database!")
    except Exception as e:
        logger.error(f"Error checking database: {str(e)}")