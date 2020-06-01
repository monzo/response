import logging
from datetime import datetime

from django.conf import settings

from response.core.models.incident import Incident
from response.slack.decorators import ActionContext, action_handler
from response.slack.dialog_builder import (
    Dialog,
    SelectFromUsers,
    SelectWithOptions,
    Text,
    TextArea,
)
from response.slack.models import CommsChannel, HeadlinePost
from response.slack.settings import INCIDENT_EDIT_DIALOG

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

    # Update the headline post to link to this
    headline_post = HeadlinePost.objects.get(incident=ac.incident)
    headline_post.comms_channel = comms_channel
    headline_post.save()


@action_handler(HeadlinePost.EDIT_INCIDENT_BUTTON)
def handle_edit_incident_button(ac: ActionContext):
    dialog_elements = [
        Text(label="Report", name="report", value=ac.incident.report),
        TextArea(
            label="Summary",
            name="summary",
            value=ac.incident.summary,
            optional=True,
            placeholder="Can you share any more details?",
        ),
        TextArea(
            label="Impact",
            name="impact",
            value=ac.incident.impact,
            optional=True,
            placeholder="Who or what might be affected?",
            hint="Think about affected people, systems, and processes",
        ),
        SelectFromUsers(
            label="Lead",
            name="lead",
            value=ac.incident.lead.external_id if ac.incident.lead else None,
            optional=True,
        ),
        SelectWithOptions(
            [(s.capitalize(), i) for i, s in Incident.SEVERITIES],
            value=ac.incident.severity,
            label="Severity",
            name="severity",
            optional=True,
        ),
    ]

    dialog = Dialog(
        title=f"Edit Incident {ac.incident.pk}",
        submit_label="Save",
        state=ac.incident.pk,
        elements=dialog_elements,
    )
    dialog.send_open_dialog(INCIDENT_EDIT_DIALOG, ac.trigger_id)
