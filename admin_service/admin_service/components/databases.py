import os

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("CINEMA_POSTGRES_DB", "cinema_db"),
        "USER": os.environ.get("CINEMA_POSTGRES_USER", "cinema_user"),
        "PASSWORD": os.environ.get("CINEMA_POSTGRES_PASSWORD"),
        "HOST": os.environ.get("POSTGRES_HOST", "127.0.0.1"),
        "PORT": os.environ.get("POSTGRES_PORT", 5432),
    },
}
