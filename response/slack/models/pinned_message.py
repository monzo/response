from datetime import datetime
from django.db import models

from response.slack.slack_utils import get_user_profile, GetOrCreateSlackExternalUser
from response.core.models import Incident, ExternalUser


class PinnedMessageManager(models.Manager):
    def add_pin(self, incident, message_ts, author_id, text):
        name = get_user_profile(author_id)['name']
        author = GetOrCreateSlackExternalUser(external_id=author_id, display_name=name)

        PinnedMessage.objects.get_or_create(
            incident=incident,
            message_ts=message_ts,
            defaults={
                'author': author,
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
    author = models.ForeignKey(ExternalUser, on_delete=models.PROTECT, blank=False, null=False)
    message_ts = models.CharField(max_length=50, blank=False, null=False)
    text = models.TextField()
    timestamp = models.DateTimeField()

    objects = PinnedMessageManager()

    def __str__(self):
        return f"{self.text}"
