"""
Database Models.
"""

from typing import ClassVar

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.models import UUIDModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, UUIDModel):
    """Custom user definition."""

    email = models.EmailField(_("Email Address"), unique=True)
    is_staff = models.BooleanField(_("Is Staff?"), default=False)
    is_active = models.BooleanField(_("Is Active?"), default=True)
    date_joined = models.DateTimeField(_("Joined Date"), default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects: ClassVar[UserManager] = UserManager()

    class Meta:
        verbose_name = "User"

    def __str__(self) -> str:
        """String representation for the model."""

        return self.email

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.
        """
        return reverse("users:detail", kwargs={"pk": self.id})
