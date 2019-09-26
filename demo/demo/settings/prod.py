import os

from .base import *  # noqa: F401, F403
from .base import SLACK_CLIENT, get_env_var

SITE_URL = os.environ.get("SITE_URL")

DEBUG = False

if os.environ.get("POSTGRES"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": os.environ.get("DB_HOST"),
            "PORT": os.environ.get("DB_PORT"),
            "USER": os.environ.get("DB_USER"),
            "NAME": os.environ.get("DB_NAME"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "SSLMODE": os.environ.get("DB_SSL_MODE"),
        }
    }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {
            "format": " {levelname:5s} - {module:10.15s} - {message}",
            "style": "{",
        }
    },
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        }
    },
}

SLACK_TOKEN = get_env_var("SLACK_TOKEN")
SLACK_SIGNING_SECRET = get_env_var("SLACK_SIGNING_SECRET")
INCIDENT_CHANNEL_NAME = get_env_var("INCIDENT_CHANNEL_NAME")
INCIDENT_REPORT_CHANNEL_NAME = get_env_var("INCIDENT_REPORT_CHANNEL_NAME")
INCIDENT_BOT_NAME = get_env_var("INCIDENT_BOT_NAME")

INCIDENT_BOT_ID = os.getenv("INCIDENT_BOT_ID") or SLACK_CLIENT.get_user_id(
    INCIDENT_BOT_NAME
)
INCIDENT_CHANNEL_ID = os.getenv("INCIDENT_CHANNEL_ID") or SLACK_CLIENT.get_channel_id(
    INCIDENT_CHANNEL_NAME
)
INCIDENT_REPORT_CHANNEL_ID = os.getenv(
    "INCIDENT_REPORT_CHANNEL_ID"
) or SLACK_CLIENT.get_channel_id(INCIDENT_REPORT_CHANNEL_NAME)
