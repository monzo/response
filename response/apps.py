from django.apps import AppConfig


class ResponseConfig(AppConfig):
    name = 'response'

    def ready(self):
        from .slack import (settings,
                       signals,
                       action_handlers,
                       event_handlers,
                       incident_commands,
                       keyword_handlers,
                       incident_notifications,
                       dialog_handlers,
                       workflows)
        if settings.PAGERDUTY_ENABLED:
            from .slack.workflows import pagerduty
