# internships/admin.py

from django.contrib import admin
from .models import (
    Internship,
    InternshipStep,
    UserInternship,
    Submission,
)  # Updated import


class InternshipStepInline(admin.TabularInline):
    """
    Allows editing InternshipSteps directly within the Internship admin page.
    """

    model = InternshipStep
    extra = 1  # Provides one empty slot for a new step.
    ordering = ("order",)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    """
    Admin view for managing Internships and their associated Steps.
    """

    inlines = [InternshipStepInline]  # Updated inline
    list_display = ("title", "field", "length_days", "created_at")
    list_filter = ("field",)
    search_fields = ("title", "description")


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "get_user_email",
        "get_internship_title",
        "submitted_at",
        "difficulty_rating",
    )
    list_filter = (
        "difficulty_rating",
        "fully_completed",
        "user_internship__internship__field",
    )
    search_fields = (
        "user_internship__user__email",
        "user_internship__internship__title",
    )
    readonly_fields = (
        "user_internship",
        "project_link",
        "fully_completed",
        "experience_feedback",
        "difficulty_rating",
        "submitted_at",
    )
    fields = (
        "user_internship",
        "project_link",
        "fully_completed",
        "experience_feedback",
        "difficulty_rating",
        "submitted_at",
        "evaluation_reason",
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("user_internship__user", "user_internship__internship")
        )

    @admin.display(description="User Email", ordering="user_internship__user__email")
    def get_user_email(self, obj):
        return obj.user_internship.user.email

    @admin.display(
        description="Internship Title", ordering="user_internship__internship__title"
    )
    def get_internship_title(self, obj):
        return obj.user_internship.internship.title


@admin.register(UserInternship)
class UserInternshipAdmin(admin.ModelAdmin):
    list_display = ("user", "internship", "status", "enrollment_date")
    list_filter = ("status", "internship__field")
    search_fields = ("user__email", "internship__title")
    list_editable = ("status",)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
