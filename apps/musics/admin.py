"""
Admin Customization For Music App.
"""

from django.contrib import admin

from apps.core.models import Music, MusicArtists


class MusicArtistsInline(admin.TabularInline):
    """Inline tabular field to select artists."""

    model = MusicArtists
    extra = 1


class MusicAdmin(admin.ModelAdmin):
    """Admin setup for music management."""

    list_display = (
        "title",
        "album_name",
        "release_date",
        "genre",
        "created",
        "modified",
    )
    date_hierarchy = "release_date"
    search_fields = ("title",)
    ordering = ("title",)
    list_filter = ("genre", "release_date")
    inlines = [
        MusicArtistsInline,
    ]


admin.site.register(Music, MusicAdmin)
