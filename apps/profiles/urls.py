"""
URLs For User Profiles.
"""

from django.urls import path

from .views import create_profile, get_profile, get_profiles, update_profile

urlpatterns = [
    path("", get_profiles, name="get_profiles"),
    path("<uuid:id>/", get_profile, name="get_profile"),
    path("create_profile/", create_profile, name="create_profile"),
    path("update_profile/<uuid:id>/", update_profile, name="update_profile"),
]
