from django.apps import AppConfig
from django.conf import settings


class SlackConfig(AppConfig):
    name = 'response.slack'

    def ready(self):
        from . import (settings,
                       signals,
                       action_handlers,
                       event_handlers,
                       incident_commands,
                       keyword_handlers,
                       incident_notifications,
                       dialog_handlers,
                       workflows)
        if settings.PAGERDUTY_ENABLED:
            from .workflows import pagerduty
