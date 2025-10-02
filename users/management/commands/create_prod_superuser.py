# users/management/commands/create_prod_superuser.py

import os
from django.core.management.base import BaseCommand, CommandError
from users.models import CustomUser


class Command(BaseCommand):
    """
    A Django management command to create a superuser from environment variables.
    It's idempotent: if the user already exists, it will not attempt to create it again.
    """

    help = "Creates a production superuser from environment variables if one does not already exist."

    def handle(self, *args, **options):
        # Read credentials from environment variables
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        # Validate that all required environment variables are set
        if not all([email, username, password]):
            raise CommandError(
                "Missing superuser credentials. Please set DJANGO_SUPERUSER_EMAIL, "
                "DJANGO_SUPERUSER_USERNAME, and DJANGO_SUPERUSER_PASSWORD environment variables."
            )

        # Check if the user already exists
        if CustomUser.objects.filter(email=email).exists():
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser '{email}' already exists. Skipping creation."
                )
            )
            return

        # Create the superuser
        self.stdout.write(f"Creating superuser '{email}'...")
        try:
            CustomUser.objects.create_superuser(
                email=email, full_name=username, password=password
            )
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created superuser '{email}'.")
            )
        except Exception as e:
            raise CommandError(f"An error occurred while creating the superuser: {e}")
