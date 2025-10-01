# internships/serializers.py

from rest_framework import serializers
from .models import Internship, Task, UserInternship, Submission

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'order']

class InternshipListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = ['id', 'title', 'thumbnail', 'field', 'length_days', 'created_at']

class InternshipDetailSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Internship
        fields = ['id', 'title', 'thumbnail', 'description', 'field', 'length_days', 'created_at', 'tasks']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            'project_link', 'fully_completed', 'experience_feedback', 
            'difficulty_rating'
        ]

class UserInternshipSerializer(serializers.ModelSerializer):
    internship = InternshipListSerializer(read_only=True)
    submission = SubmissionSerializer(read_only=True)
    
    class Meta:
        model = UserInternship
        # --- THE 'is_started' FIELD IS NOW INCLUDED HERE ---
        fields = [
            'id', 'internship', 'enrollment_date', 'status', 
            'is_started', 'intro_completed', 'roadmap_completed', 'submission'
        ]