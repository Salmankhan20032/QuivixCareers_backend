# internships/admin.py

from django.contrib import admin
from .models import Internship, Task, UserInternship, Submission

class TaskInline(admin.TabularInline):
    """
    Allows editing Tasks directly within the Internship admin page.
    """
    model = Task
    extra = 1 # Provides one empty slot for a new task.
    ordering = ('order',)


@admin.register(Internship)
class InternshipAdmin(admin.ModelAdmin):
    """
    Admin view for managing Internships and their associated Tasks.
    """
    inlines = [TaskInline]
    list_display = ('title', 'field', 'length_days', 'created_at')
    list_filter = ('field',)
    search_fields = ('title', 'description')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    """
    Admin view for reviewing user Submissions.
    The admin can view all submitted data and add an evaluation reason.
    """
    list_display = ('get_user_email', 'get_internship_title', 'submitted_at', 'difficulty_rating')
    list_filter = ('difficulty_rating', 'fully_completed', 'user_internship__internship__field')
    search_fields = ('user_internship__user__email', 'user_internship__internship__title')
    
    # User-submitted fields should not be changed by the admin.
    readonly_fields = ('user_internship', 'project_link', 'fully_completed', 
                       'experience_feedback', 'difficulty_rating', 'submitted_at')
    
    # The 'evaluation_reason' field is left editable for the admin to provide feedback.
    fields = ('user_internship', 'project_link', 'fully_completed', 
              'experience_feedback', 'difficulty_rating', 'submitted_at', 
              'evaluation_reason')
              
    def get_queryset(self, request):
        # Optimize database queries by pre-fetching related objects.
        return super().get_queryset(request).select_related('user_internship__user', 'user_internship__internship')

    @admin.display(description='User Email', ordering='user_internship__user__email')
    def get_user_email(self, obj):
        return obj.user_internship.user.email
    
    @admin.display(description='Internship Title', ordering='user_internship__internship__title')
    def get_internship_title(self, obj):
        return obj.user_internship.internship.title


@admin.register(UserInternship)
class UserInternshipAdmin(admin.ModelAdmin):
    """
    Admin view for managing User Enrollments in Internships.
    This is where the admin will Accept or Reject a user's progress.
    """
    list_display = ('user', 'internship', 'status', 'enrollment_date')
    list_filter = ('status', 'internship__field')
    search_fields = ('user__email', 'internship__title')
    
    # Make status editable directly in the list view for quick actions.
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        # This override ensures our signals logic is correctly triggered when
        # the model is saved through the admin panel. The signal itself
        # handles the notification creation.
        super().save_model(request, obj, form, change)