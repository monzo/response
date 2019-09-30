from datetime import datetime

from django.db import models

from response.core.models import ExternalUser, Incident, TimelineEvent
from response.core.serializers import ExternalUserSerializer
from response.slack.cache import get_user_profile


class PinnedMessageManager(models.Manager):
    def add_pin(self, incident, message_ts, author_id, text):
        name = get_user_profile(author_id)["name"]
        author, _ = ExternalUser.objects.get_or_create_slack(
            external_id=author_id, display_name=name
        )
        timestamp = datetime.fromtimestamp(float(message_ts))

        user_data = ExternalUserSerializer(author).data

        timeline_event = TimelineEvent(
            incident=incident,
            timestamp=timestamp,
            text=text,
            event_type="slack_pin",
            metadata={
                "author": user_data,
                "message_ts": message_ts,
                "channel_id": incident.comms_channel().channel_id,
            },
        )
        timeline_event.save()

        PinnedMessage.objects.get_or_create(
            incident=incident,
            message_ts=message_ts,
            defaults={
                "author": author,
                "text": text,
                "timestamp": timestamp,
                "timeline_event": timeline_event,
            },
        )

    def remove_pin(self, incident, message_ts):
        timestamp = datetime.fromtimestamp(float(message_ts))
        TimelineEvent.objects.filter(incident=incident, timestamp=timestamp).delete()
        PinnedMessage.objects.filter(incident=incident, message_ts=message_ts).delete()


class PinnedMessage(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    author = models.ForeignKey(
        ExternalUser, on_delete=models.PROTECT, blank=False, null=False
    )
    message_ts = models.CharField(max_length=50, blank=False, null=False)
    text = models.TextField()
    timestamp = models.DateTimeField()

    objects = PinnedMessageManager()
    timeline_event = models.ForeignKey(
        TimelineEvent, on_delete=models.CASCADE, null=True
    )

    def __str__(self):
        return f"{self.text}"
