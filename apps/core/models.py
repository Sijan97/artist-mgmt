"""
Database Models.
"""

from typing import ClassVar

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from model_utils.models import TimeStampedModel, UUIDModel

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, UUIDModel, TimeStampedModel):
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
        """String representation of the model."""

        return self.email

    def get_absolute_url(self) -> str:
        """Get URL for user's detail view.

        Returns:
            str: URL for user detail.
        """
        return reverse("users:detail", kwargs={"pk": self.id})


class Profile(UUIDModel, TimeStampedModel):
    """Base profile definition."""

    GENDER_CHOICES = Choices("male", "female", "others")

    def validate_date(value):
        """Validate date of birth."""
        if value > timezone.now():
            raise ValidationError(_("Date must not be greater than present."))

    date_of_birth = models.DateTimeField(_("Date of Birth"), null=True, blank=True, validators=[validate_date])
    gender = models.CharField(_("Gender"), choices=GENDER_CHOICES, default=GENDER_CHOICES.male)
    address = models.CharField(_("Full Address"), max_length=255, null=True, blank=True)

    class Meta:
        abstract = True


class UserProfile(Profile):
    """User profile definition."""

    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name="profile")
    first_name = models.CharField(_("First Name"), max_length=50, null=True, blank=True)
    last_name = models.CharField(_("Last Name"), max_length=50, null=True, blank=True)
    phone = models.CharField(_("Phone Number"), max_length=15, null=True, blank=True)

    class Meta:
        verbose_name = "User Profile"

    def __str__(self) -> str:
        """String representation of the model."""

        return f"{self.first_name}'s Profile" if self.first_name else f"{self.user}"

    def get_absolute_url(self) -> str:
        """Get URL for user's profile detail view."""

        return reverse("user_profile:detail", kwargs={"pk": self.id})


class ArtistProfile(Profile):
    """Artist's profile definition."""

    name = models.CharField(_("Name"), max_length=50, null=True, blank=True)
    first_release_year = models.IntegerField(_("First Release Year"), null=True, blank=True)
    no_of_albums_released = models.IntegerField(_("Number of Albums Released"), null=True, blank=True)

    class Meta:
        verbose_name = "Artist Profile"

    def __str__(self) -> str:
        """String representation of the model."""

        return f"{self.name}" if self.name else ""

    def get_absolute_url(self) -> str:
        """Get URL for artist's profile detail view."""

        return reverse("artist_profile:detail", kwargs={"pk": self.id})


class Music(UUIDModel, TimeStampedModel):
    """Database model definition for music."""

    GENRE_CHOICES = Choices("rnb", "country", "classic", "rock", "jazz", "pop")

    def validate_date(value):
        """Validate date of birth."""
        if value > timezone.now():
            raise ValidationError(_("Release date must not be greater than present."))

    artists = models.ManyToManyField(ArtistProfile, related_name="musics", through="MusicArtists")
    title = models.CharField(_("Title"), max_length=100, null=True, blank=True)
    album_name = models.CharField(_("Album Name"), max_length=100, null=True, blank=True)
    release_date = models.DateTimeField(_("Release Date"), null=True, blank=True, validators=[validate_date])
    genre = models.CharField(_("Genre"), max_length=8, choices=GENRE_CHOICES, default=GENRE_CHOICES.rnb)

    class Meta:
        verbose_name = "Music"

    def __str__(self) -> str:
        """String representation of the model."""

        return self.title

    def get_absolute_url(self) -> str:
        """Get URL for music detail view."""

        return reverse("music:detail", kwargs={"pk": self.id})


class MusicArtists(UUIDModel):
    """Custom intermediatary table for music and artists."""

    music = models.ForeignKey("Music", null=True, blank=True, on_delete=models.SET_NULL)
    artistprofile = models.ForeignKey("ArtistProfile", null=True, blank=True, on_delete=models.SET_NULL)

    class Meta:
        db_table = "core_music_artists"
        verbose_name = "Music Artist"
        verbose_name_plural = "Music Artists"
