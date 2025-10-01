# users/urls.py
from django.urls import path
from .views import RegisterView, UserProfileView, VerifyOTPView, ResendOTPView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Auth flow
    path("register/", RegisterView.as_view(), name="register"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),
    path("resend-otp/", ResendOTPView.as_view(), name="resend_otp"),
    path(
        "login/", TokenObtainPairView.as_view(), name="token_obtain_pair"
    ),  # Standard login is still available
    path("login/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User data
    path("profile/", UserProfileView.as_view(), name="user_profile"),
]
