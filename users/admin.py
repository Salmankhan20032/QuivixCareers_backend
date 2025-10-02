from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
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
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    readonly_fields = ("last_login", "date_joined")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "profile_picture_preview",
        "university",
        "major",
        "interest",
    )

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="50" />', obj.profile_picture.url)
        return "-"

    profile_picture_preview.short_description = "Profile Picture"


admin.site.register(CustomUser, CustomUserAdmin)
