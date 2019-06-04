import json
from datetime import datetime

from django.conf import settings
from slack.settings import INCIDENT_EDIT_DIALOG
from core.models.incident import Incident
from slack.dialog_builder import Dialog, Text, TextArea, SelectWithOptions, SelectFromUsers
from slack.models import HeadlinePost, CommsChannel
from slack.slack_utils import invite_user_to_channel, get_slack_token_owner, leave_channel, archive_channel

from slack.decorators import action_handler


@action_handler(HeadlinePost.CLOSE_INCIDENT_BUTTON)
def handle_close_incident(incident: Incident, user_id: str, message: json, trigger_id: str):
    incident.end_time = datetime.now()
    # incident.save()
    try:
        if CommsChannel.objects.filter(incident=incident).exists():
            chan = CommsChannel.objects.get(incident=incident)
            if chan is not None:
                print(chan.channel_id)
                leave_channel(chan.channel_id)
                archive_channel(chan.channel_id)
                incident.save()
    except Exception as e:
        print(str(e))
        pass




@action_handler(HeadlinePost.CREATE_COMMS_CHANNEL_BUTTON)
def handle_create_comms_channel(incident: Incident, user_id: str, message: json, trigger_id: str):
    if CommsChannel.objects.filter(incident=incident).exists():
        return

    comms_channel = CommsChannel.objects.create_comms_channel(incident)

    # Invite the bot to the channel
    invite_user_to_channel(settings.INCIDENT_BOT_ID, comms_channel.channel_id)

     # Invite the Reporter to the channel
    invite_user_to_channel(incident.reporter, comms_channel.channel_id)

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


@action_handler(HeadlinePost.EDIT_INCIDENT_BUTTON)
def handle_edit_incident_button(incident: Incident, user_id: str, message: json, trigger_id: str):
    dialog = Dialog(
        title=f"Edit Incident {incident.pk}",
        submit_label="Save",
        state=incident.pk,
        elements=[
            Text(label="Report", name="report", value=incident.report),
            TextArea(label="Summary", name="summary", value=incident.summary, optional=True, placeholder="Can you share any more details?"),
            TextArea(label="Impact", name="impact", value=incident.impact, optional=True, placeholder="Who or what might be affected?", hint="Think about affected people, systems, and processes"),
            SelectFromUsers(label="Lead", name="lead", value=incident.lead, optional=True),
            SelectWithOptions([(i, s.capitalize()) for i, s in Incident.SEVERITIES], value=incident.severity, label="Severity", name="severity", optional=True)
        ]
    )

    dialog.send_open_dialog(INCIDENT_EDIT_DIALOG, trigger_id)
