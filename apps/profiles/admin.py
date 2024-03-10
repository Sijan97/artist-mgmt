"""
Admin Customization For User Profile App.
"""

from django.contrib import admin

from apps.core.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    """Admin setup for user profile management."""

    list_display = (
        "user",
        "full_name",
        "date_of_birth",
        "gender",
        "phone",
        "created",
        "modified",
    )
    date_hierarchy = "date_of_birth"
    search_fields = ("first_name",)
    ordering = ("first_name",)
    list_filter = ("gender",)

    def full_name(self, obj: UserProfile):
        """Returns full name for the profile."""

        return f"{obj.first_name} {obj.last_name}"


admin.site.register(UserProfile, UserProfileAdmin)
