from datetime import datetime

from response.core.models import Action, Event, Incident
from response.core.serializers import ActionSerializer, IncidentSerializer

from django.db.models.signals import post_save
from django.dispatch import receiver

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Action)
def emit_action_event(sender, instance: Action, **kwargs):
    logger.info(f"Handling post_save for action: {instance}")

    event = Event()
    event.event_type = Event.ACTION_EVENT_TYPE

    # Event payload should be a dict for serializing to JSON.
    event.payload = ActionSerializer(instance).data
    event.payload["incident_id"] = instance.incident.pk
    # TODO: define a serializer that elides this field (otherwise
    # it is returned in incident responses too)
    if "details_ui" in event.payload: del event.payload["details_ui"]

    event.timestamp = datetime.now(tz=None)
    event.save()


@receiver(post_save, sender=Incident)
def emit_incident_event(sender, instance: Incident, **kwargs):
    logger.info(f"Handling post_save for incident: {instance}")

    event = Event()
    event.event_type = Event.INCIDENT_EVENT_TYPE

    # Event payload should be a dict for serializing to JSON.
    event.payload = IncidentSerializer(instance).data

    event.timestamp = datetime.now(tz=None)
    event.save()
