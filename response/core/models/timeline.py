from datetime import datetime
from django.db import models
from jsonfield import JSONField

from response.core.models.incident import Incident


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
    event_type = models.CharField(max_length=10, help_text="Type of event.")
    metadata = JSONField(
        help_text="Additional fields that can be added by other event types", null=True
    )

