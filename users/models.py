# users/models.py
from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import random


class CustomUserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault(
            "is_verified", True
        )  # Superusers should be verified by default
        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)  # is_active is now just for banning
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)  # <-- OUR NEW VERIFICATION FIELD!
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return self.email


class UserProfile(models.Model):
    class InterestChoices(models.TextChoices):
        WEB_DEV = "Web Development", "Web Development"
        MOBILE_DEV = "Mobile App Development", "Mobile App Development"
        GAME_DEV = "Game Development", "Game Development"
        DATA_SCIENCE = "Data Science / AI", "Data Science / AI"
        CLOUD_DEVOPS = "Cloud & DevOps", "Cloud & DevOps"

    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="profile"
    )
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    university = models.CharField(max_length=200, blank=True, null=True)
    major = models.CharField(max_length=200, blank=True, null=True)
    interest = models.CharField(
        max_length=50, choices=InterestChoices.choices, blank=True, null=True
    )

    def __str__(self):
        return f"{self.user.full_name}'s Profile"


# Signal to create a UserProfile automatically when a CustomUser is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    # Check if a profile exists to avoid errors on initial creation
    if hasattr(instance, "profile"):
        instance.profile.save()


# --- NEW OTP MODEL ---
class OTP(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    otp_code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        # OTPs will be valid for 10 minutes
        return timezone.now() > self.created_at + timedelta(minutes=10)

    def __str__(self):
        return f"OTP for {self.user.email}: {self.otp_code}"
