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
        if obj.thumbnail and hasattr(obj.thumbnail, "public_id"):
            return cloudinary_url(obj.thumbnail.public_id)[0]
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
        fields = [
            "id",
            "internship",
            "enrollment_date",
            "status",
            "is_started",
            "intro_completed",
            "roadmap_completed",
            "submission",
            "completed_steps",  # <-- THIS FIELD IS NOW INCLUDED
        ]
