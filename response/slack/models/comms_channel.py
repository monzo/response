import logging
from datetime import datetime
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
        time_string = datetime.now().strftime("%b-%-e-%H-%M-%S")
        name = f"inc-{time_string}".lower()

        try:
            channel_id = settings.SLACK_CLIENT.get_or_create_channel(
                name, auto_unarchive=True
            )
        except SlackError as e:
            logger.error(f"Failed to create comms channel {e}")
            raise

        # If the channel already existed we will need to join it
        # If we are already in the channel as we created it, then this is a No-Op
        try:
            logger.info(f"Joining channel {name}")
            settings.SLACK_CLIENT.join_channel(name)
        except SlackError as e:
            logger.error(f"Failed to join comms channel {e}")
            raise

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
            raise

        comms_channel = self.create(
            incident=incident, channel_id=channel_id, channel_name=name
        )
        return comms_channel


class CommsChannel(models.Model):

    objects = CommsChannelManager()
    incident = models.OneToOneField(Incident, on_delete=models.CASCADE)
    channel_id = models.CharField(max_length=20, null=False)
    channel_name = models.CharField(max_length=80, null=False)

    def post_in_channel(self, message: str):
        settings.SLACK_CLIENT.send_message(self.channel_id, message)

    def rename(self, new_name):
        if new_name:
            try:
                response = settings.SLACK_CLIENT.rename_channel(
                    self.channel_id, new_name
                )
                self.channel_name = response["channel"]["name"]
                self.save()
            except SlackError as e:
                logger.error(
                    f"Failed to rename channel {self.channel_id} to {new_name}. Error: {e}"
                )
                raise e
        else:
            logger.info("Attempted to rename channel to nothing. No action take.")

    def __str__(self):
        return self.incident.report
