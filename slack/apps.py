from django.apps import AppConfig


class SlackConfig(AppConfig):
    name = 'slack'

    def ready(self):
        import slack.signals
        import slack.action_handlers
        import slack.event_handlers
        import slack.incident_commands
        import slack.keyword_handlers
        import slack.incident_notifications
