# internships/models.py

from django.db import models
from django.conf import settings
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver
from cloudinary.models import CloudinaryField

FIELD_CHOICES = [
    ("Web Development", "Web Development"),
    ("Mobile App Development", "Mobile App Development"),
    ("Game Development", "Game Development"),
    ("Data Science / AI", "Data Science / AI"),
    ("Cloud & DevOps", "Cloud & DevOps"),
]


class Internship(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = CloudinaryField("thumbnail", null=True, blank=True)
    description = models.TextField()
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)
    length_days = models.PositiveIntegerField(
        help_text="Duration of the internship in days"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class InternshipStep(models.Model):
    class StepType(models.TextChoices):
        LEARN = "learn", "Learning Material"
        TASK = "task", "Task & Submission"

    internship = models.ForeignKey(
        Internship, related_name="steps", on_delete=models.CASCADE
    )
    step_type = models.CharField(
        max_length=10, choices=StepType.choices, default=StepType.LEARN
    )
    title = models.CharField(max_length=200)
    content = models.TextField(
        blank=True, help_text="Main content for a 'Learning' step."
    )
    external_link = models.URLField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional: A link to a PDF, video, or article for a 'Learning' step.",
    )
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.internship.title} - Step {self.order}: {self.title}"


class UserInternship(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "In Progress"
        AWAITING_EVALUATION = "awaiting_evaluation", "Awaiting Evaluation"
        ACCEPTED = "accepted", "Accepted"
        REJECTED = "rejected", "Rejected"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_PROGRESS
    )
    is_started = models.BooleanField(default=False)

    # --- THIS IS THE PERSISTENT PROGRESS FIELD ---
    completed_steps = models.ManyToManyField(
        InternshipStep, blank=True, related_name="completed_by"
    )

    intro_completed = models.BooleanField(default=False)
    roadmap_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ("user", "internship")

    def __str__(self):
        return f"{self.user.email} enrolled in {self.internship.title}"


class Submission(models.Model):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MID = "mid", "Medium"
        HARD = "hard", "Hard"

    user_internship = models.OneToOneField(
        UserInternship, on_delete=models.CASCADE, related_name="submission"
    )
    project_link = models.URLField(max_length=500)
    fully_completed = models.BooleanField()
    experience_feedback = models.TextField(blank=True, null=True)
    difficulty_rating = models.CharField(max_length=10, choices=Difficulty.choices)
    submitted_at = models.DateTimeField(auto_now_add=True)
    evaluation_reason = models.TextField(
        blank=True, null=True, help_text="Reason for rejection, if any."
    )

    def __str__(self):
        return f"Submission for {self.user_internship}"


@receiver(pre_save, sender=Internship)
def delete_old_thumbnail(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        old_instance = Internship.objects.get(pk=instance.pk)
    except Internship.DoesNotExist:
        return
    if old_instance.thumbnail and old_instance.thumbnail != instance.thumbnail:
        try:
            old_instance.thumbnail.delete(save=False)
        except Exception:
            pass


@receiver(post_delete, sender=Internship)
def delete_thumbnail_on_delete(sender, instance, **kwargs):
    if instance.thumbnail:
        try:
            instance.thumbnail.delete(save=False)
        except Exception:
            pass
