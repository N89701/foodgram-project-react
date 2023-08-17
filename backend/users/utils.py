from django.core.exceptions import ValidationError


def validate_username(value):
    if value == 'me':
        raise ValidationError("Value 'me' is not available for username")
