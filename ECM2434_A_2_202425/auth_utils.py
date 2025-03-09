from rest_framework_simplejwt.authentication import JWTAuthentication

def custom_user_authentication_rule(user):
    """
    Custom function to ensure the user is active and valid for authentication
    """
    return user is not None and user.is_active

class CustomJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        """
        Override to add role from token to the user object
        """
        user = super().get_user(validated_token)
        
        # Add role from token to user object if it exists
        if user is not None and 'role' in validated_token:
            user.role = validated_token['role']
            
        return user