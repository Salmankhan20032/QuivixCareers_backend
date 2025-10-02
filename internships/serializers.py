# internships/serializers.py

from rest_framework import serializers
from .models import (
    Internship,
    InternshipStep,
    UserInternship,
    Submission,
)  # Updated import
from cloudinary.models import CloudinaryField
from cloudinary.utils import cloudinary_url


class InternshipStepSerializer(serializers.ModelSerializer):
    """
    Serializer for the new InternshipStep model.
    """

    class Meta:
        model = InternshipStep
        fields = ["id", "title", "step_type", "content", "external_link", "order"]


class InternshipListSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    class Meta:
        model = Internship
        fields = ["id", "title", "thumbnail", "field", "length_days", "created_at"]

    def get_thumbnail(self, obj):
        if obj.thumbnail:
            url, options = cloudinary_url(obj.thumbnail.public_id)
            return url
        return None


class InternshipDetailSerializer(serializers.ModelSerializer):
    # --- UPDATED: Use the new step serializer ---
    steps = InternshipStepSerializer(many=True, read_only=True)

    class Meta:
        model = Internship
        fields = [
            "id",
            "title",
            "thumbnail",
            "description",
            "field",
            "length_days",
            "created_at",
            "steps",  # Changed from "tasks" to "steps"
        ]


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = [
            "project_link",
            "fully_completed",
            "experience_feedback",
            "difficulty_rating",
        ]


class UserInternshipSerializer(serializers.ModelSerializer):
    internship = InternshipListSerializer(read_only=True)
    submission = SubmissionSerializer(read_only=True)

    class Meta:
        model = UserInternship
        # --- THE 'is_started' FIELD IS NOW INCLUDED HERE ---
        fields = [
            "id",
            "internship",
            "enrollment_date",
            "status",
            "is_started",
            "intro_completed",
            "roadmap_completed",
            "submission",
        ]
