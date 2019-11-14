import logging
from datetime import datetime

from django.conf import settings
from django.db.models.signals import post_save
from django.utils.module_loading import import_string

from response.core.models import Action, Event, Incident
from response.core.serializers import ActionSerializer, IncidentSerializer

logger = logging.getLogger(__name__)


class ActionEventHandler:
    @staticmethod
    def handle(sender, instance: Action, **kwargs):
        if instance.incident.private:
            logger.info(f"Skipping action post_save for private incident: {instance}")
            return
        logger.info(f"Handling post_save for action: {instance}")

        event = Event()
        event.event_type = Event.ACTION_EVENT_TYPE

        # Event payload should be a dict for serializing to JSON.
        event.payload = ActionSerializer(instance).data
        event.payload["incident_id"] = instance.incident.pk
        if "details_ui" in event.payload:
            del event.payload["details_ui"]

        event.timestamp = datetime.now(tz=None)
        event.save()


class IncidentEventHandler:
    @staticmethod
    def handle(sender, instance: Incident, **kwargs):
        if instance.private:
            logger.info(f"Skipping incident post_save for private incident: {instance}")
            return
        logger.info(f"Handling post_save for incident: {instance}")

        event = Event()
        event.event_type = Event.INCIDENT_EVENT_TYPE

        # Event payload should be a dict for serializing to JSON.
        event.payload = IncidentSerializer(instance).data
        # Actions generate their own events, no need to duplicate them here.
        if "action_items" in event.payload:
            del event.payload["action_items"]

        event.timestamp = datetime.now(tz=None)
        event.save()


if hasattr(settings, "ACTION_EVENT_HANDLER_CLASS"):
    cls = import_string(settings.ACTION_EVENT_HANDLER_CLASS)
    post_save.connect(cls.handle, sender=Action)
else:
    post_save.connect(ActionEventHandler.handle, sender=Action)

if hasattr(settings, "INCIDENT_EVENT_HANDLER_CLASS"):
    cls = import_string(settings.INCIDENT_EVENT_HANDLER_CLASS)
    post_save.connect(cls.handle, sender=Incident)
else:
    post_save.connect(IncidentEventHandler.handle, sender=Incident)
