from datetime import datetime
from django.conf import settings
from django.db import models

from core.models.incident import Incident

from slack.slack_utils import get_or_create_channel, send_message, SlackError, rename_channel
from slack.block_kit import *

import logging
logger = logging.getLogger(__name__)


class CommsChannelManager(models.Manager):
    def create_comms_channel(self, incident):
        "Creates a comms channel in slack, and saves a reference to it in the DB"
        try:
            name = f"inc-{100+incident.pk}"
            channel_id = get_or_create_channel(name)
        except SlackError as e:
            logger.error('Failed to create comms channel {e}')

        comms_channel = self.create(
            incident=incident,
            channel_id=channel_id,
        )
        return comms_channel


class CommsChannel(models.Model):

    objects = CommsChannelManager()
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    channel_id = models.CharField(max_length=20, null=False)

    def post_in_channel(self, message: str):
        send_message(self.channel_id, message)

    def rename(self, new_name):
        rename_channel(self.channel_id, new_name)
