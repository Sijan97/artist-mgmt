from .base import *

# Toggle Debug Mode
DEBUG = True

# Django Debug Toolbar
INSTALLED_APPS += ["debug_toolbar"]

MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]

DEBUG_TOOLBAR_CONFIG = {
    "DISABLE_PANELS": ["debug_toolbar.panels.redirects.RedirectsPanel"],
    "SHOW_TEMPLATE_CONTEXT": True,
}

# Allowed Hosts Definition
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

CORS_ORIGIN_WHITELIST = (
    "http://localhost:3000",
    "http://127.0.0.1:3000",
)

CSRF_TRUSTED_ORIGINS = ["http://localhost", "http://127.0.0.1"]


# Local Database Configuration
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env("DEV_DB_NAME"),
        "USER": env("DEV_DB_USER"),
        "PASSWORD": env("DEV_DB_PASSWORD"),
        "HOST": "localhost",
        "PORT": 5432,
    }
}
