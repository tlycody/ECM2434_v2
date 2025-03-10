# Import the base AppConfig class from Django's apps module
from django.apps import AppConfig


# Define a configuration class for the "bingo" app
class BingoConfig(AppConfig):
    # Set the default field type for auto-generated primary keys
    default_auto_field = "django.db.models.BigAutoField"
    
    # Define the name of the app as "bingo"
    name = "bingo"
    
    def ready(self):
        # Import signals when the app is ready
        import bingo.signals