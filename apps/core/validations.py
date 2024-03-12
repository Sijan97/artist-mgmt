"""
Custom Validations.
"""

import datetime

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import dateparse, timezone
from rest_framework.response import Response


def email_validation(email: str) -> bool:
    """Validate email."""

    try:
        validate_email(email)

        return True
    except ValidationError:
        return False


def password_validation(password: str) -> bool:
    """Validate password"""

    try:
        validate_password(password)

        return True
    except ValidationError:
        return False


def date_validation(date_str: datetime) -> bool:
    """Validate date."""

    parsed_date = dateparse.parse_datetime(date_str)

    if not timezone.is_aware(parsed_date):
        parsed_date = timezone.make_aware(parsed_date)

    if parsed_date > timezone.now():
        return False

    return True


def integer_validation(num: int) -> bool:
    """Validate integer value."""

    try:
        parsed_num = int(num)

        if parsed_num < 0:
            return False

        return True
    except ValidationError:
        return Response({"message": "Please enter a valid number."})
