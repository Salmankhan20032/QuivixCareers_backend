# internships/models.py

from django.db import models
from django.conf import settings

# Choices for fields, aligning with UserProfile interests
FIELD_CHOICES = [
    ('Web Development', 'Web Development'),
    ('Mobile App Development', 'Mobile App Development'),
    ('Game Development', 'Game Development'),
    ('Data Science / AI', 'Data Science / AI'),
    ('Cloud & DevOps', 'Cloud & DevOps'),
]

class Internship(models.Model):
    title = models.CharField(max_length=200)
    thumbnail = models.ImageField(upload_to='internship_thumbnails/')
    description = models.TextField()
    field = models.CharField(max_length=50, choices=FIELD_CHOICES)
    length_days = models.PositiveIntegerField(help_text="Duration of the internship in days")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(models.Model):
    internship = models.ForeignKey(Internship, related_name='tasks', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(help_text="Detailed instructions for the task")
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.internship.title} - Task {self.order}: {self.title}"

class UserInternship(models.Model):
    class Status(models.TextChoices):
        IN_PROGRESS = 'in_progress', 'In Progress'
        AWAITING_EVALUATION = 'awaiting_evaluation', 'Awaiting Evaluation'
        ACCEPTED = 'accepted', 'Accepted'
        REJECTED = 'rejected', 'Rejected'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    internship = models.ForeignKey(Internship, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.IN_PROGRESS)
    
    # Progress tracking fields
    is_started = models.BooleanField(default=False) # <-- THE NEW FIELD FOR MEMORY
    intro_completed = models.BooleanField(default=False)
    roadmap_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'internship') # A user can only apply to an internship once

    def __str__(self):
        return f"{self.user.email} enrolled in {self.internship.title}"

class Submission(models.Model):
    class Difficulty(models.TextChoices):
        EASY = 'easy', 'Easy'
        MID = 'mid', 'Medium'
        HARD = 'hard', 'Hard'
    
    user_internship = models.OneToOneField(UserInternship, on_delete=models.CASCADE, related_name='submission')
    project_link = models.URLField(max_length=500)
    fully_completed = models.BooleanField()
    experience_feedback = models.TextField(blank=True, null=True)
    difficulty_rating = models.CharField(max_length=10, choices=Difficulty.choices)
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    # For admin feedback
    evaluation_reason = models.TextField(blank=True, null=True, help_text="Reason for rejection, if any.")

    def __str__(self):
        return f"Submission for {self.user_internship}"