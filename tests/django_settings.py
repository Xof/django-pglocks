import os

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("PGDATABASE", "django_pglocks"),
        "USER": os.environ.get("PGUSER", "django_pglocks"),
        "PASSWORD": os.environ.get("PGPASSWORD", "django_pglocks"),
        "HOST": os.environ.get("PGHOST", "localhost"),
        "PORT": os.environ.get("PGPORT", "5432"),
    },
}

INSTALLED_APPS: list[str] = []

SECRET_KEY = "test-secret-key-not-for-production"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
