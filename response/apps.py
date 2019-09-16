from django.apps import AppConfig
from django.conf import settings as site_settings
from django.templatetags.static import static
from django.utils.functional import lazy


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

        self.configure_setting("RESPONSE_LOGIN_REQUIRED", True)
        self.configure_setting("RESPONSE_APP_NAME", "Response")
        self.configure_setting(
            "RESPONSE_FAVICON", self.lazy_static_url("images/favicon.png")
        )
        self.configure_setting(
            "RESPONSE_LOGO", self.lazy_static_url("images/response.png")
        )

    def configure_setting(self, name, default):
        setattr(site_settings, name, getattr(site_settings, name, default))

    def lazy_static_url(self, name):
        return lazy(lambda: static(name))()
