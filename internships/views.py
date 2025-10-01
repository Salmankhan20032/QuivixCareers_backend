# internships/views.py

from rest_framework import generics, permissions, status
from rest_framework.filters import SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Internship, UserInternship, Submission
from .serializers import (
    InternshipListSerializer, InternshipDetailSerializer, 
    UserInternshipSerializer, SubmissionSerializer
)

class InternshipListView(generics.ListAPIView):
    """
    Lists all available internships.
    Includes search functionality across title, description, and field.
    """
    queryset = Internship.objects.all().order_by('-created_at')
    serializer_class = InternshipListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['title', 'description', 'field']


class InternshipDetailView(generics.RetrieveAPIView):
    """
    Retrieves the detailed view of a single internship, including its tasks.
    """
    queryset = Internship.objects.all()
    serializer_class = InternshipDetailSerializer
    permission_classes = [permissions.IsAuthenticated]


class ApplyInternshipView(APIView):
    """
    Handles a user's request to apply for/enroll in an internship.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            internship = Internship.objects.get(pk=pk)
        except Internship.DoesNotExist:
            return Response({"error": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user has already applied
        if UserInternship.objects.filter(user=request.user, internship=internship).exists():
            return Response({"error": "You have already applied for this internship."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create the enrollment record for the user
        user_internship = UserInternship.objects.create(user=request.user, internship=internship)
        serializer = UserInternshipSerializer(user_internship)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MyInternshipsView(generics.ListAPIView):
    """
    Lists all internships the currently authenticated user has applied for.
    """
    serializer_class = UserInternshipSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return UserInternship.objects.filter(user=self.request.user).order_by('-enrollment_date')


class UpdateInternshipProgressView(APIView):
    """
    Allows a user to update their progress on an internship (e.g., mark intro/roadmap as done).
    Handles PATCH requests to persist progress.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, pk):
        try:
            # Find the specific enrollment record for the logged-in user
            user_internship = UserInternship.objects.get(pk=pk, user=request.user)
        except UserInternship.DoesNotExist:
            return Response({"error": "Enrollment record not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserInternshipSerializer(user_internship, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmitInternshipView(APIView):
    """
    Handles the final submission of a user's project for an internship.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            user_internship = UserInternship.objects.get(pk=pk, user=request.user)
        except UserInternship.DoesNotExist:
            return Response({"error": "Enrollment record not found."}, status=status.HTTP_404_NOT_FOUND)

        if user_internship.status != 'in_progress':
             return Response({"error": f"Cannot submit, internship is already {user_internship.get_status_display()}."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            # Create the submission linked to the user's enrollment
            serializer.save(user_internship=user_internship)
            
            # Update the status of the enrollment to 'Awaiting Evaluation'
            user_internship.status = UserInternship.Status.AWAITING_EVALUATION
            user_internship.save()
            
            # Return the updated UserInternship record
            response_serializer = UserInternshipSerializer(user_internship)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)