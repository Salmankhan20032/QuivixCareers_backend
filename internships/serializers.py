# internships/serializers.py

from rest_framework import serializers
from .models import Internship, InternshipStep, UserInternship, Submission
from cloudinary.utils import cloudinary_url


class InternshipStepSerializer(serializers.ModelSerializer):
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
            "steps",
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
        # --- aDDED 'completed_steps' TO THE aSERIALIZER ---
        # This will send a list of completed step IDs to the frontend.
        fields = [
            "id",
            "internship",
            "enrollment_date",
            "status",
            "is_started",
            "intro_completed",  # Kept for compatibility
            "roadmap_completed",  # Kept for compatibility
            "submission",
            "completed_steps",  # This is the new, important field
        ]
