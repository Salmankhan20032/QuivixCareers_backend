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
        # Added evaluation_reason so frontend can display it
        fields = [
            "id",
            "project_link",
            "fully_completed",
            "experience_feedback",
            "difficulty_rating",
            "submitted_at",
            "evaluation_reason",
        ]


class UserInternshipSerializer(serializers.ModelSerializer):
    internship = InternshipListSerializer(read_only=True)

    # --- UPDATED: To handle multiple submissions, we only show the latest one ---
    latest_submission = serializers.SerializerMethodField()

    class Meta:
        model = UserInternship
        fields = [
            "id",
            "internship",
            "enrollment_date",
            "status",
            "is_started",
            "completed_steps",
            "latest_submission",
        ]

    def get_latest_submission(self, obj):
        # Because we added ordering to the Submission model, .first() gives the newest one.
        latest = obj.submissions.first()
        if latest:
            return SubmissionSerializer(latest).data
        return None
