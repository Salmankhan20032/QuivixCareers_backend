# users/views.py

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

# --- THE MISSING IMPORT IS ADDED BACK HERE, MY LOVE! ---
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer
from .models import (
    CustomUser,
    OTP,
    UserProfile,
)  # Also good to explicitly import UserProfile
from .utils import send_otp_email
from django.utils import timezone
import random

# For generating tokens manually after verification
from rest_framework_simplejwt.tokens import RefreshToken


class RegisterView(generics.CreateAPIView):
    """
    Handle user registration.
    Creates an unverified user and sends an OTP to their email.
    """

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.is_verified = False  # Ensure user is not verified by default
        user.save()

        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, otp_code=otp_code)

        send_otp_email(user, otp_code)


class VerifyOTPView(APIView):
    """
    Verify the OTP sent to the user's email.
    If successful, mark the user as verified and log them in by returning JWT tokens.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_code = request.data.get("otp")

        if not email or not otp_code:
            return Response(
                {"error": "Email and OTP are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            user = CustomUser.objects.get(email=email)
            otp = OTP.objects.filter(user=user, otp_code=otp_code).latest("created_at")

            if otp.is_expired():
                return Response(
                    {"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            user.is_verified = True
            user.save()
            OTP.objects.filter(user=user).delete()

            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(
                user, context={"request": request}
            )  # Pass context

            return Response(
                {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                    "user": user_serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except OTP.DoesNotExist:
            return Response(
                {"error": "Invalid OTP."}, status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ResendOTPView(APIView):
    """
    Resend a new OTP to a user's email if their previous one expired.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        if not email:
            return Response(
                {"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            user = CustomUser.objects.get(email=email)
            if user.is_verified:
                return Response(
                    {"error": "This account is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            OTP.objects.filter(user=user).delete()

            otp_code = str(random.randint(100000, 999999))
            OTP.objects.create(user=user, otp_code=otp_code)
            send_otp_email(user, otp_code)

            return Response(
                {"success": "A new OTP has been sent to your email."},
                status=status.HTTP_200_OK,
            )
        except CustomUser.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )


class UserProfileView(APIView):
    """
    Handles retrieving and updating the logged-in user's profile information.
    Combines data from CustomUser and UserProfile models.
    """

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = self.serializer_class(request.user, context={"request": request})
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        profile = user.profile

        user_data = {
            "full_name": request.data.get("full_name", user.full_name),
            "nationality": request.data.get("nationality", user.nationality),
        }

        profile_data = request.data.copy()
        profile_data.pop("full_name", None)
        profile_data.pop("nationality", None)
        profile_data.pop("email", None)

        user_serializer = UserSerializer(
            instance=user, data=user_data, partial=True, context={"request": request}
        )
        profile_serializer = UserProfileSerializer(
            instance=profile,
            data=profile_data,
            partial=True,
            context={"request": request},
        )

        is_user_valid = user_serializer.is_valid()
        is_profile_valid = profile_serializer.is_valid()

        if is_user_valid and is_profile_valid:
            user_serializer.save()
            profile_serializer.save()

            final_serializer = self.serializer_class(user, context={"request": request})
            return Response(final_serializer.data, status=status.HTTP_200_OK)

        errors = {**user_serializer.errors, **profile_serializer.errors}
        return Response(errors, status=status.HTTP_400_BAD_REQUEST)
