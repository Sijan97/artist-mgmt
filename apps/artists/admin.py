"""
Admin Customization For Artist Profile App.
"""

from django.contrib import admin

from apps.core.models import ArtistProfile


class ArtistProfileAdmin(admin.ModelAdmin):
    """Admin setup for artist profile management."""

    list_display = (
        "name",
        "date_of_birth",
        "gender",
        "first_release_year",
        "no_of_albums_released",
        "created",
        "modified",
    )
    date_hierarchy = "date_of_birth"
    search_fields = ("name",)
    ordering = ("name",)
    list_filter = ("gender", "first_release_year")


admin.site.register(ArtistProfile, ArtistProfileAdmin)
