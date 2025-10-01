# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserProfile


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profile"
    fk_name = "user"


class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ("email", "full_name", "is_verified", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_verified", "groups")
    search_fields = ("email", "full_name", "nationality")
    ordering = ("email",)

    # We still define the layout using fieldsets
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "nationality")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        # The fields are still listed here for layout purposes
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # --- THE FIX IS HERE, MY LOVE! ---
    # This line tells Django to display these two fields as non-editable text.
    readonly_fields = ("last_login", "date_joined")


admin.site.register(CustomUser, CustomUserAdmin)
