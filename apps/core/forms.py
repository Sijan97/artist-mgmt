"""
Use custom user for user creation and change form.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from django.contrib.auth import get_user_model


user_model = get_user_model()


class CustomUserCreationForm(UserCreationForm):
    """Custom user creation form."""

    email = forms.EmailField(max_length=254, help_text="Enter a valid email address")

    class Meta:
        model = user_model
        fields = (
            "email",
            "password1",
            "password2",
        )


class CustomUserChangeForm(UserChangeForm):
    """Custom user change form."""

    class Meta:
        modle = user_model
        fields = ("email",)
