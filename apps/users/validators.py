import re

from rest_framework.exceptions import ValidationError


def validate_phone_number(value):
    pattern = r'^\+998\d{9}$'
    if not re.match(pattern, value):
        raise ValidationError("The phone number must start with '+998' and be followed by 9 digits!")
