import json
import after_response

from response.core.models import Incident


from response.slack.block_kit import Message, Section, Divider, Text, Button
from response.slack.dialog_builder import Dialog, Text as DialogText
from response.slack.action_handlers import action_handler, ActionContext
from response.slack.dialog_handlers import dialog_handler
from response.slack.incident_commands import incident_command
from response.slack.slack_utils import user_reference
from response.slack.models import CommsChannel, HeadlinePost

from response.pagerduty.models import Escalation
from response.pagerduty.incident import trigger_incident
import pypd

from django.conf import settings

import logging
logger = logging.getLogger(__name__)


PAGE_SPECIALIST_DIALOG = "page_specialist_dialog"
ESCALATE_BUTTON = "escalate_button_id"


def incident_key(incident):
    return f"monzo-incident-{incident.pk}"


@action_handler(HeadlinePost.PAGE_ON_CALL_BUTTON)
def headline_post_handle_page_oncall_engineer(context: ActionContext):
    key = incident_key(context.incident)
    trigger_incident(context.incident.report, key, details=context.incident.summary)


@incident_command(['escalate', 'esc'], helptext='Escalate to someone else')
def handle_escalatations(incident: Incident, user_id: str, message: str):
    escalations = Escalation.objects.all()

    if not escalations:
        msg = Message()
        msg.add_block(Section(text=Text("No specialists have been configured 😢")))
    else:
        msg = Message()
        msg.add_block(Section(text=Text("Let's find the right people to help you out 🔍")))
        msg.add_block(Divider())
        msg.add_block(Section(text=Text("These are the teams available as escalations:")))

        for team in escalations:
            team_section = Section(
                text=Text(f"*{team.name}*\n{team.summary}"),
                accessory=Button(f"📟 Page {team.name}", ESCALATE_BUTTON, value=f"{team.name}")
            )
            msg.add_block(team_section)

        msg.add_block(Divider())
        msg.add_block(Section(text=Text("Not sure who to pick? Press the page button in #incidents!")))

    comms_channel = CommsChannel.objects.get(incident=incident)
    msg.send(comms_channel.channel_id)

    return True, None


@action_handler(ESCALATE_BUTTON)
def handle_page_oncall_engineer(context: ActionContext):
    dialog = Dialog(
        title=f"Escalate to a specialist",
        submit_label="Escalate",
        elements=[
            DialogText(label="Message", name="message", placeholder=f"Why do you need {context.button_value}?", hint="You might be waking this person up.  Please make this friendly and clear."),
        ],
        state=context.button_value
    )

    dialog.send_open_dialog(PAGE_SPECIALIST_DIALOG, context.trigger_id)
    return True


@dialog_handler(PAGE_SPECIALIST_DIALOG)
def page_specialist_dialog(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    try:
        comms_channel = CommsChannel.objects.get(channel_id=channel_id)
        incident = comms_channel.incident
    except CommsChannel.DoesNotExist:
        logger.error(f"Couldn't find comms channel with id {channel_id}")
        return

    specialist = Escalation.objects.get(name=state)
    message = submission['message']

    page_specialist(incident, specialist, message)
    return


def page_specialist(incident: Incident, escalation: Escalation, message: str):
    # check if a pagerduty incident exists
    key = incident_key(incident)
    pd_incident = next(iter(pypd.Incident.find(incident_key=key)), None)

    if pd_incident:
        # existing pagerduty incident found so reassign to the specialists
        from_user = pypd.User.find_one(email=settings.PAGERDUTY_DEFAULT_EMAIL)
        pd_incident.add_responders(settings.PAGERDUTY_DEFAULT_EMAIL, from_user.id, message, escalation_policy_ids=[escalation.escalation_policy])
    else:
        # no existing pagerduty incident so trigger one directly for the specialists
        trigger_incident(message, key, details=incident.summary, escalation_policy=escalation.escalation_policy)

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f"👋 Sit tight. I've escalated to the {escalation.name} team.")
