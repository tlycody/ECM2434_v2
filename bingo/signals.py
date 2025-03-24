
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.apps import apps

@receiver(post_migrate)
def create_special_users(sender, **kwargs):
    """
    Creates special users (gamekeeper and developer) after migrations are completed
    This ensures they exist when the server starts
    """
    if sender.name != 'bingo':  
        return
    
    # Avoid circular imports
    User = apps.get_model('bingo', 'User')  
    
    # Special passwords from your form
    GAMEKEEPER_PASSWORD = "MYPASS123"
    DEVELOPER_PASSWORD = "MYDEV123"
    
    # Create gamekeeper user if it doesn't exist
    if not User.objects.filter(username='GAMEKEEPER').exists():
        gamekeeper = User.objects.create_user(
            username='GAMEKEEPER',
            email='mk811@exeter.ac.uk',
            password="MYPASS123"
        )
        gamekeeper.role = 'Game Keeper'
        gamekeeper.is_staff = True
        gamekeeper.save()
        print("Created gamekeeper user")
    
    # Create developer user if it doesn't exist
    if not User.objects.filter(username='DEVELOPER').exists():
        developer = User.objects.create_user(
            username='DEVELOPER',
            email='myosandarkyaw22@gmail.com',
            password="MYDEV123"
        )
        developer.role = 'Developer'
        developer.is_staff = True 
        developer.is_superuser = True
        developer.save()
        print("Created developer user")
        
        pass