from django.apps import AppConfig


class ResponseConfig(AppConfig):
    name = 'response'

    def ready(self):
        from .slack import (settings,
                            signals,
                            action_handlers,
                            event_handlers,
                            incident_commands,
                            incident_notifications,
                            dialog_handlers)
