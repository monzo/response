from datetime import datetime
from django.db import models

from slack.slack_utils import get_user_profile, GetOrCreateSlackExternalUser
from core.models import Incident, ExternalUser, Timeline


class PinnedMessageManager(models.Manager):
    def add_pin(self, incident, message_ts, author_id, text):
        author = GetOrCreateSlackExternalUser(external_id=author_id)

        timeline = Timeline.objects.new_event(
            editable=False,
            source="slack_pin",
            incident=incident,
            author=author,
            text=text,
            timestamp=datetime.fromtimestamp(float(message_ts)),
        )

        return PinnedMessage.objects.get_or_create(
            timeline=timeline,
            message_ts=message_ts,
        )

    def remove_pin(self, incident, message_ts):
        pinned_message = PinnedMessage.objects.get(
            message_ts=message_ts,
        )
        pinned_message.timeline.delete()
        pinned_message.delete()

class PinnedMessage(models.Model):
    timeline = models.ForeignKey(Timeline, on_delete=models.CASCADE)
    message_ts = models.CharField(max_length=50, blank=False, null=False)

    objects = PinnedMessageManager()

    def __str__(self):
        return f"{self.message_ts}: {self.timeline.text}"
