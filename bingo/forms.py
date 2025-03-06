# forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """
    Custom user registration form with role selection and preset passwords
    for admin roles (Game Keeper and Developer).
    """
    
    # Remove password fields for admin roles
    password1 = forms.CharField(widget=forms.PasswordInput(), required=False)
    password2 = forms.CharField(widget=forms.PasswordInput(), required=False)
    
    # Add admin password field that's only shown to admins
    admin_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=False,
        label="Admin Password"
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'role')
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        admin_password = cleaned_data.get('admin_password')
        
        # Define the special passwords for admin roles
        GAMEKEEPER_PASSWORD = "GameKeeper2025!"
        DEVELOPER_PASSWORD = "DevTeam2025!"
        
        if role == 'Game Keeper':
            # Check if the entered admin password matches Game Keeper password
            if admin_password != GAMEKEEPER_PASSWORD:
                self.add_error('admin_password', "Incorrect Game Keeper password")
            else:
                # Set the actual user password to this special password
                cleaned_data['password1'] = GAMEKEEPER_PASSWORD
                cleaned_data['password2'] = GAMEKEEPER_PASSWORD
        
        elif role == 'Developer':
            # Check if the entered admin password matches Developer password
            if admin_password != DEVELOPER_PASSWORD:
                self.add_error('admin_password', "Incorrect Developer password")
            else:
                # Set the actual user password to this special password
                cleaned_data['password1'] = DEVELOPER_PASSWORD
                cleaned_data['password2'] = DEVELOPER_PASSWORD
        
        else:  # Regular player
            # For players, require them to create their own password
            if not cleaned_data.get('password1'):
                self.add_error('password1', "This field is required.")
            if not cleaned_data.get('password2'):
                self.add_error('password2', "This field is required.")
            
        return cleaned_data
    
    