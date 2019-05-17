from .base import *

SITE_URL =  os.environ.get("TUNNEL_HOSTNAME")

if os.environ.get("POSTGRES"):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'HOST': os.environ.get("DB_HOST"),
            'PORT': '5432',
            'USER': os.environ.get("DB_USER"),
            'NAME': os.environ.get("DB_NAME"),
            'PASSWORD': os.environ.get("DB_PASSWORD"),
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

try:
    INCIDENT_BOT_ID = get_user_id(INCIDENT_BOT_NAME, SLACK_TOKEN)
except:
    INCIDENT_BOT_ID = None

try:
    INCIDENT_CHANNEL_ID = get_channel_id(INCIDENT_CHANNEL_NAME, SLACK_TOKEN)
except:
    INCIDENT_CHANNEL_ID = None
