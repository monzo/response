import logging
from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.urls import reverse

from response.core.models.incident import Incident
from response.slack.client import SlackError

logger = logging.getLogger(__name__)


class CommsChannelManager(models.Manager):
    def create_comms_channel(self, incident):
        """
        Creates a comms channel in slack, and saves a reference to it in the DB
        """
        try:
            name = f"inc-{100+incident.pk}"
            channel_id = settings.SLACK_CLIENT.get_or_create_channel(
                name, auto_unarchive=True
            )
        except SlackError as e:
            logger.error(f"Failed to create comms channel {e}")

        try:
            doc_url = urljoin(
                settings.SITE_URL,
                reverse("incident_doc", kwargs={"incident_id": incident.pk}),
            )

            settings.SLACK_CLIENT.set_channel_topic(
                channel_id, f"{incident.report} - {doc_url}"
            )
        except SlackError as e:
            logger.error(f"Failed to set channel topic {e}")

        comms_channel = self.create(incident=incident, channel_id=channel_id)
        return comms_channel


class CommsChannel(models.Model):

    objects = CommsChannelManager()
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    channel_id = models.CharField(max_length=20, null=False)

    def post_in_channel(self, message: str):
        settings.SLACK_CLIENT.send_message(self.channel_id, message)

    def rename(self, new_name):
        settings.SLACK_CLIENT.rename_channel(self.channel_id, new_name)

    def channel_name(self):
        return settings.SLACK_CLIENT.get_channel_name(self.channel_id)

    def __str__(self):
        return self.incident.report
