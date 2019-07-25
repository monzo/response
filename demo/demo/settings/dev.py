from .base import *

SITE_URL = "http://localhost:8000"

if os.environ.get("POSTGRES"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': 'db',
            'PORT': '5432',
            'USER': 'postgres',
            'NAME': 'postgres',
        }
    }


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': " {levelname:5s} - {module:10.15s} - {message}",
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': os.getenv('DJANGO_LOG_LEVEL', 'INFO'),
            'propagate': False,
        },
    },
}


SLACK_TOKEN = get_env_var("SLACK_TOKEN")
SLACK_SIGNING_SECRET = get_env_var("SLACK_SIGNING_SECRET")
INCIDENT_CHANNEL_NAME = get_env_var("INCIDENT_CHANNEL_NAME")
INCIDENT_BOT_NAME = get_env_var("INCIDENT_BOT_NAME")

SLACK_API_MOCK = os.getenv("SLACK_API_MOCK", None)

INCIDENT_BOT_ID = os.getenv("INCIDENT_BOT_ID") or SLACK_CLIENT.get_user_id(INCIDENT_BOT_NAME)
INCIDENT_CHANNEL_ID = os.getenv("INCIDENT_CHANNEL_ID") or SLACK_CLIENT.get_channel_id(INCIDENT_CHANNEL_NAME)
