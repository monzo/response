import json

from django.db import models


class Event(models.Model):
    ACTION_EVENT_TYPE = "action_event"
    INCIDENT_EVENT_TYPE = "incident_event"

    timestamp = models.DateTimeField()
    event_type = models.CharField(max_length=50)
    payload = models.TextField()

    def save(self, *args, **kwargs):
        self.payload = json.dumps(self.payload)
        super().save(*args, **kwargs)
