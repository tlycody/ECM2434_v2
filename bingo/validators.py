#Strong Password Function
#Must special letter, upper case, lower case, digit

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class CustomPasswordValidator:
    @staticmethod
    def validate(password, user=None):
        conditions = [
            (any(char.isdigit() for char in password), _('Password must contain at least one digit.')),
            (any(char.isalpha() for char in password), _('Password must contain at least one letter.')),
            (any(char.isupper() for char in password), _('Password must contain at least one uppercase letter.')),
            (any(char.islower() for char in password), _('Password must contain at least one lowercase letter.')),
            (any(char in '!@#$%^&*()_+' for char in password), _('Password must contain at least one special character: !@#$%^&*()_+'))
        ]

        errors = [ValidationError(_(message)) for condition, message in conditions if not condition]

        if errors:
            raise ValidationError(errors)

    @staticmethod
    def get_help_text():
        return _(
            "Your password must contain at least one digit, one letter, one uppercase letter, one lowercase letter, and one special character: !@#$%^&*()_+"
        )
