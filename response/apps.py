from django.apps import AppConfig
from django.conf import settings as site_settings


class ResponseConfig(AppConfig):
    name = "response"

    def ready(self):
        from .slack import (  # noqa: F401
            settings,
            signals,
            action_handlers,
            event_handlers,
            incident_commands,
            incident_notifications,
            dialog_handlers,
        )

        from .core import signals as core_signals  # noqa: F401

        site_settings.RESPONSE_LOGIN_REQUIRED = getattr(
            site_settings, "RESPONSE_LOGIN_REQUIRED", True
        )

        for template in site_settings.TEMPLATES:
            context_processors = template.get("OPTIONS", {}).get("context_processors")
            if context_processors:
                context_processors.append("response.core.context_processors.site")
