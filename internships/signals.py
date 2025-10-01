# internships/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import UserInternship
from notifications.models import Notification # Import Notification model

@receiver(post_save, sender=UserInternship)
def create_notification_on_status_change(sender, instance, created, **kwargs):
    # We only care about updates, not new enrollments
    if created:
        return

    # Check if the 'status' field was updated.
    # A simple way is to just create a notification based on the new status.
    if instance.status == 'awaiting_evaluation':
        Notification.objects.create(
            user=instance.user,
            message=f"Your submission for '{instance.internship.title}' is now awaiting evaluation.",
            related_internship=instance
        )
    elif instance.status == 'accepted':
        Notification.objects.create(
            user=instance.user,
            message=f"Congratulations! Your submission for '{instance.internship.title}' has been accepted.",
            related_internship=instance
        )
    elif instance.status == 'rejected':
        reason = instance.submission.evaluation_reason if hasattr(instance, 'submission') and instance.submission.evaluation_reason else "Please review the requirements."
        Notification.objects.create(
            user=instance.user,
            message=f"Your submission for '{instance.internship.title}' needs revision. Reason: {reason}",
            related_internship=instance
        )