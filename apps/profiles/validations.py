"""
Custom Validations.
"""

import datetime

from django.utils import dateparse, timezone


def date_of_birth_validation(date_str: datetime) -> bool:
    """Validate date of birth."""

    parsed_date = dateparse.parse_datetime(date_str)

    if not timezone.is_aware(parsed_date):
        parsed_date = timezone.make_aware(parsed_date)

    if parsed_date > timezone.now():
        return False

    return True
