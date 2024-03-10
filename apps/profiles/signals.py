"""
Post save signal to create a default profile for a user.
"""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.core.models import UserProfile


@receiver(post_save, sender=get_user_model())
def create_profile_handler(sender, instance, created, **kwargs):  # noqa
    """Create new profile during creation of new user."""

    if not created:
        return

    profile = UserProfile(user=instance)
    profile.save()
