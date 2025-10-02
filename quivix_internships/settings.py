import os
from pathlib import Path
from datetime import timedelta
import dj_database_url
from dotenv import load_dotenv
import cloudinary

# --- BASE DIRECTORY ---
BASE_DIR = Path(__file__).resolve().parent.parent

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv(os.path.join(BASE_DIR, ".env"))

# --- SECURITY SETTINGS ---
SECRET_KEY = os.getenv("SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "api-quivix.onrender.com",
]

CSRF_TRUSTED_ORIGINS = ["https://api-quivix.onrender.com"]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://careers.quivixdigital.com",
    "https://quivixcareers.netlify.app",
]

# --- SSL & PROXY SETTINGS ---
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG

# --- APPLICATION DEFINITION ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
    "cloudinary_storage",
    "cloudinary",
    "users",
    "internships",
    "notifications",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

# --- DATABASE (NEON POSTGRES) ---
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required!")

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
        ssl_require=True,
    )
}

# Explicit SSL mode for psycopg
DATABASES["default"]["OPTIONS"] = {"sslmode": "require"}

# --- AUTH SETTINGS ---
AUTH_USER_MODEL = "users.CustomUser"
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- STATIC FILES ---
STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# --- MEDIA & CLOUDINARY ---
CLOUDINARY_URL = os.getenv("CLOUDINARY_URL")
if not CLOUDINARY_URL:
    raise ValueError("CLOUDINARY_URL environment variable is required!")

cloudinary_config = cloudinary.config(cloudinary_url=CLOUDINARY_URL)

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": cloudinary_config.cloud_name,
    "API_KEY": cloudinary_config.api_key,
    "API_SECRET": cloudinary_config.api_secret,
}

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
MEDIA_URL = "/media/"

# --- DEFAULT FIELD TYPE ---
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- REST FRAMEWORK & JWT ---
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    )
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

# --- THIRD-PARTY SERVICE KEYS ---
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
