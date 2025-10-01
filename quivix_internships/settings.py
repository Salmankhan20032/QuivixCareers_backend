# quivix_internships/settings.py

import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- Load environment variables from .env file ---
# Create a .env file in the root directory (next to manage.py) for local development
load_dotenv(os.path.join(BASE_DIR, ".env"))


# --- Quick-start development settings - unsuitable for production ---

# SECRET_KEY is read from an environment variable for security.
# The default value is insecure and should only be used for local development.
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-default-key-for-local-dev")

# DEBUG should be False in production!
# It's read from the .env file. For production, set DEBUG=False or remove the variable.
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

# Add your production domain name(s) and 'localhost' for local testing.
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "https://api-quivix.onrender.com/"]


# --- Application definition ---

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party apps
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "cloudinary_storage",  # For Cloudinary media storage
    "cloudinary",  # For Cloudinary API
    # Our awesome apps
    "users",
    "whitenoise.runserver_nostatic",  # <-- ADD THIS! Useful for testing static files locally
    "internships",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # <-- ADD THIS LINE, MY LOVE!
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # Should be placed high, before CommonMiddleware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "quivix_internships.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "quivix_internships.wsgi.application"


# --- Database ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
# Uses dj_database_url to parse the DATABASE_URL environment variable (for services like Neon, Heroku).
# Falls back to local SQLite if DATABASE_URL is not set.

if "DATABASE_URL" in os.environ:
    DATABASES = {"default": dj_database_url.config(conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# --- User and Password Validation ---

# Tell Django to use our custom user model
AUTH_USER_MODEL = "users.CustomUser"

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# --- Internationalization ---
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# --- Static files (CSS, JavaScript, Images) ---
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "static/"
# Directory where 'collectstatic' will gather all static files for production.
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"  # <-- ADD THIS LINE
)

# --- Media files (User uploaded content) ---
# In production, these will be handled by Cloudinary.

# This tells Django to use Cloudinary for all media file uploads.
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = "/media/"
# Local media root, useful for local development if not using Cloudinary locally.
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Cloudinary credentials are read from environment variables.
# The CLOUDINARY_URL environment variable is often used, but explicit settings also work.
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}


# --- Default primary key field type ---
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# --- Django Rest Framework Settings ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

# --- Simple JWT Settings ---
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}


# --- CORS (Cross-Origin Resource Sharing) Settings ---
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # Your local React app
    "https://your-frontend-production-url.com",  # Add your frontend's live URL
]
# You can also use CORS_ALLOW_ALL_ORIGINS = True for initial testing, but it's insecure.


# --- Third-Party Service Keys ---
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "YOUR_BREVO_V3_API_KEY_HERE")
