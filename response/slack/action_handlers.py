import logging
from datetime import datetime

from django.conf import settings

from response.core.models.incident import Incident
from response.slack import block_kit
from response.slack.decorators import ActionContext, action_handler
from response.slack.dialog_builder import (
    Dialog,
    SelectFromUsers,
    SelectWithOptions,
    Text,
    TextArea,
)
from response.slack.models import CommsChannel, HeadlinePost
from response.slack.report_flow import edit_incident

logger = logging.getLogger(__name__)


@action_handler(HeadlinePost.CLOSE_INCIDENT_BUTTON)
def handle_close_incident(ac: ActionContext):
    ac.incident.end_time = datetime.now()
    ac.incident.save()


@action_handler(HeadlinePost.CREATE_COMMS_CHANNEL_BUTTON)
def handle_create_comms_channel(ac: ActionContext):
    if CommsChannel.objects.filter(incident=ac.incident).exists():
        return

    comms_channel = CommsChannel.objects.create_comms_channel(ac.incident)

    # Invite the bot to the channel
    try:
        settings.SLACK_CLIENT.invite_user_to_channel(
            settings.INCIDENT_BOT_ID, comms_channel.channel_id
        )
    except Exception as ex:
        logger.error(ex)

    # Un-invite the user who owns the Slack token,
    #   otherwise they'll be added to every incident channel
    slack_token_owner = settings.SLACK_CLIENT.get_slack_token_owner()
    if ac.incident.reporter != slack_token_owner:
        settings.SLACK_CLIENT.leave_channel(comms_channel.channel_id)

    # Update the headline post to link to this
    headline_post = HeadlinePost.objects.get(incident=ac.incident)
    headline_post.comms_channel = comms_channel
    headline_post.save()


@action_handler(HeadlinePost.EDIT_INCIDENT_BUTTON)
def handle_edit_incident_button(ac: ActionContext):
    edit_incident(ac.incident, ac.trigger_id)
