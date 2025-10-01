# notifications/models.py
from django.db import models
from django.conf import settings

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional: A link to a related object, e.g., the internship
    related_internship = models.ForeignKey(
        'internships.UserInternship', 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user.email}: {self.message}"