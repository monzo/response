import json
from datetime import datetime

from django.conf import settings
from core.models.incident import Incident
from slack.models import HeadlinePost, CommsChannel
from slack.slack_utils import invite_user_to_channel, get_slack_token_owner, leave_channel

from slack.decorators.action_handler import action_handler


@action_handler(HeadlinePost.CLOSE_INCIDENT_BUTTON)
def handle_close_incident(incident: Incident, user_id: str, message: json) -> json:
    incident.end_time = datetime.now()
    incident.save()


@action_handler(HeadlinePost.CREATE_COMMS_CHANNEL_BUTTON)
def handle_create_comms_channel(incident: Incident, user_id: str, message: json) -> json:
    if CommsChannel.objects.filter(incident=incident).exists():
        return

    comms_channel = CommsChannel.objects.create_comms_channel(incident)

    # Invite the bot to the channel
    invite_user_to_channel(settings.INCIDENT_BOT_ID, comms_channel.channel_id)

    # Un-invite the user who owns the Slack token,
    #   otherwise they'll be added to every incident channel
    slack_token_owner = get_slack_token_owner()
    if incident.reporter != slack_token_owner:
        leave_channel(comms_channel.channel_id)

    # Update the headline post to link to this
    headline_post = HeadlinePost.objects.get(
        incident=incident
    )
    headline_post.comms_channel = comms_channel
    headline_post.save()
