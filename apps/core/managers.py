"""
Custom Managers.
"""

from typing import TYPE_CHECKING

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    user = get_user_model()


class UserManager(BaseUserManager["user"]):
    """Manager for custom user with email as username field."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """
        Create and save a user with the given email and password.
        """
        if not email:
            msg = "The given email must be set"
            raise ValueError(msg)

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password, **extra_fields):
        """Create, save and return a new user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create, save and return a new superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff set to True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser set to True."))

        return self._create_user(email, password, **extra_fields)
