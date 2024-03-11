"""
URLs For Artist Profile.
"""

from django.urls import path

from .views import create_artist, delete_artist, get_artist, get_artists, update_artist

urlpatterns = [
    path("", get_artists, name="get_artists"),
    path("<uuid:id>/", get_artist, name="get_artist"),
    path("create_artist/", create_artist, name="create_artist"),
    path("update_artist/<uuid:id>/", update_artist, name="update_artist"),
    path("delete_artist/<uuid:id>/", delete_artist, name="delete_artist"),
]
