# users/views.py

from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, UserSerializer, UserProfileSerializer
from .models import CustomUser, OTP, UserProfile
from .utils import send_otp_email
from django.utils import timezone
import random
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
            if user.is_verified:
                return Response(
                    {"error": "This account is already verified."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            otp = OTP.objects.filter(user=user, otp_code=otp_code).latest("created_at")

            if otp.is_expired():
                return Response(
                    {"error": "OTP has expired."}, status=status.HTTP_400_BAD_REQUEST
                )

            user.is_verified = True
            user.save()
            OTP.objects.filter(user=user).delete()

            refresh = RefreshToken.for_user(user)
            user_serializer = UserSerializer(user, context={"request": request})

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
        """
        --- UPDATED AND SIMPLIFIED ---
        This method now robustly updates both CustomUser and UserProfile models
        from a single API call, handling partial data from onboarding or the full
        profile form correctly.
        """
        user = request.user
        profile = user.profile

        # 1. Update the CustomUser fields directly from the request data.
        #    Use current user data as a fallback if a field isn't provided.
        user.full_name = request.data.get("full_name", user.full_name)
        user.nationality = request.data.get("nationality", user.nationality)
        user.save(update_fields=["full_name", "nationality"])

        # 2. Use the UserProfileSerializer to handle the nested profile data.
        #    The serializer will automatically ignore fields it doesn't recognize
        #    (like 'full_name'), which makes this very clean.
        profile_serializer = UserProfileSerializer(
            instance=profile,
            data=request.data,
            partial=True,
            context={"request": request},
        )

        if profile_serializer.is_valid(raise_exception=True):
            profile_serializer.save()

            # 3. After saving everything, serialize the updated user object
            #    and send it back as the response.
            final_serializer = self.serializer_class(user, context={"request": request})
            return Response(final_serializer.data, status=status.HTTP_200_OK)

        # The 'raise_exception=True' handles the error case, but this is a fallback.
        return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
