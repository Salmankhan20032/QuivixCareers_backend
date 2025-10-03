# internships/views.py

from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Internship, UserInternship, Submission, InternshipStep
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
    queryset = Internship.objects.all().prefetch_related("steps")
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
        return Response(
            UserInternshipSerializer(user_internship).data,
            status=status.HTTP_201_CREATED,
        )


class MyInternshipsView(generics.ListAPIView):
    serializer_class = UserInternshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            UserInternship.objects.filter(user=self.request.user)
            .order_by("-enrollment_date")
            .prefetch_related("completed_steps", "submissions")
        )


class UpdateInternshipProgressView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            user_internship = UserInternship.objects.get(pk=pk, user=request.user)
        except UserInternship.DoesNotExist:
            return Response(
                {"error": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        step_id = request.data.get("completed_step_id")
        if step_id:
            try:
                step = InternshipStep.objects.get(
                    pk=step_id, internship=user_internship.internship
                )
                user_internship.completed_steps.add(step)
                return Response(
                    UserInternshipSerializer(user_internship).data,
                    status=status.HTTP_200_OK,
                )
            except InternshipStep.DoesNotExist:
                return Response(
                    {"error": "Step not found."}, status=status.HTTP_404_NOT_FOUND
                )

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
                {"error": "Enrollment not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # --- THE FIX FOR RESUBMISSION ---
        # Allow submission if status is 'in_progress' OR 'rejected'.
        allowed_statuses = ["in_progress", "rejected"]
        if user_internship.status not in allowed_statuses:
            return Response(
                {
                    "error": f"Cannot submit now. Status is '{user_internship.get_status_display()}'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Create a NEW submission object.
            serializer.save(user_internship=user_internship)
            # ALWAYS set the status to Awaiting Evaluation after any submission.
            user_internship.status = UserInternship.Status.AWAITING_EVALUATION
            user_internship.save(update_fields=["status"])
            return Response(
                UserInternshipSerializer(user_internship).data,
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
