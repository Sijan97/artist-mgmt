"""
URLs For Music API.
"""

from django.urls import path

from .views import create_music, delete_music, get_music, get_music_by_artist, get_musics, update_music

urlpatterns = [
    path("", get_musics, name="get_musics"),
    path("<uuid:id>/", get_music, name="get_music"),
    path("by_artist/<uuid:artist_id>", get_music_by_artist, name="get_music_by_artist"),
    path("create_music/", create_music, name="create_music"),
    path("update/<uuid:id>", update_music, name="update_music"),
    path("delete/<uuid:id>/", delete_music, name="delete_music"),
]
