# internships/views.py

from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import (
    Internship,
    UserInternship,
    Submission,
    InternshipStep,
)  # <-- IMPORT InternshipStep
from .serializers import (
    InternshipListSerializer,
    InternshipDetailSerializer,
    UserInternshipSerializer,
    SubmissionSerializer,
)


class InternshipListView(generics.ListAPIView):
    queryset = Internship.objects.all().order_by("-created_at")
    serializer_class = InternshipListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ["title", "description", "field"]


class InternshipDetailView(generics.RetrieveAPIView):
    queryset = Internship.objects.all()
    serializer_class = InternshipDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class ApplyInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            return Response(
                {"error": "Internship not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if UserInternship.objects.filter(
            user=request.user, internship=internship
        ).exists():
            return Response(
                {"error": "You have already applied."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_internship = UserInternship.objects.create(
            user=request.user, internship=internship
        )
        serializer = UserInternshipSerializer(user_internship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyInternshipsView(generics.ListAPIView):
    serializer_class = UserInternshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # <-- OPTIMIZED: Pre-fetch related steps to avoid extra database queries -->
        return (
            UserInternship.objects.filter(user=self.request.user)
            .order_by("-enrollment_date")
            .prefetch_related("completed_steps")
        )


class UpdateInternshipProgressView(APIView):
    """
    Handles saving progress for an internship, like completing a step.
    """

    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            user_internship = UserInternship.objects.get(pk=pk, user=request.user)
        except UserInternship.DoesNotExist:
            return Response(
                {"error": "Enrollment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # <-- NEW LOGIC: Specifically handle saving a completed step -->
        step_id = request.data.get("completed_step_id")
        if step_id:
            try:
                step_to_complete = InternshipStep.objects.get(
                    pk=step_id, internship=user_internship.internship
                )
                user_internship.completed_steps.add(step_to_complete)
                # Note: No need for user_internship.save() after using .add()
                # We'll re-serialize the object to return the updated state
                serializer = UserInternshipSerializer(user_internship)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except InternshipStep.DoesNotExist:
                return Response(
                    {"error": f"Step with id {step_id} not found."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Fallback for other potential PATCH requests (e.g., legacy is_started)
        serializer = UserInternshipSerializer(
            user_internship, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitInternshipView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            user_internship = UserInternship.objects.get(pk=pk, user=request.user)
        except UserInternship.DoesNotExist:
            return Response(
                {"error": "Enrollment record not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if user_internship.status != "in_progress":
            return Response(
                {
                    "error": f"Cannot submit, internship is already {user_internship.get_status_display()}."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user_internship=user_internship)
            user_internship.status = UserInternship.Status.AWAITING_EVALUATION
            user_internship.save()
            response_serializer = UserInternshipSerializer(user_internship)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
