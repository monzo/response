from datetime import datetime

from django.db import models
from jsonfield import JSONField

from response.core.models.incident import Incident
from response.core.util import sanitize

EVENT_TYPES = (
    ("text", "Freeform text field"),
    ("slack_pin", "A message pinned from Slack"),
)


class TimelineEvent(models.Model):

    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(
        null=False, default=datetime.now, help_text="Time of when this event occurred."
    )
    text = models.TextField(help_text="Freeform text describing this event")
    event_type = models.CharField(max_length=30, help_text="Type of event.")
    metadata = JSONField(
        help_text="Additional fields that can be added by other event types", null=True
    )

    def save(self, *args, **kwargs):
        self.text = sanitize(self.text)
        super(TimelineEvent, self).save(*args, **kwargs)


def add_incident_update_event(
    incident, update_type, old_value, new_value, text, timestamp=None
):

    if not timestamp:
        timestamp = datetime.now()

    timeline_event = TimelineEvent(
        incident=incident,
        timestamp=timestamp,
        text=text,
        event_type="incident_update",
        metadata={
            "update_type": update_type,
            "old_value": old_value,
            "new_value": new_value,
        },
    )
    timeline_event.save()
