from datetime import datetime
from django.db import models

from core.models import Incident
from . import SlackUser


class PinnedMessageManager(models.Manager):
    def add_pin(self, incident, message_ts, author_id, text):
        PinnedMessage.objects.get_or_create(
            incident=incident,
            message_ts=message_ts,
            defaults={
                'author_id': author_id,
                'text': text,
                'timestamp': datetime.fromtimestamp(float(message_ts)),
            }
        )

    def remove_pin(self, incident, message_ts):
        PinnedMessage.objects.filter(
            incident=incident,
            message_ts=message_ts,
        ).delete()


class PinnedMessage(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    author_id = models.ForeignKey(SlackUser, on_delete=models.PROTECT, blank=False, null=False)
    message_ts = models.CharField(max_length=50, blank=False, null=False)
    text = models.TextField()
    timestamp = models.DateTimeField()

    objects = PinnedMessageManager()

    def __str__(self):
        return f"{self.text}"
