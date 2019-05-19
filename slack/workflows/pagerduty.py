import json
import pypd
import after_response

from core.models import Incident

from pagerduty.models import Escalation

from slack.block_kit import Message, Section, Divider, Text, Button
from slack.action_handlers import action_handler
from slack.dialog_handlers import dialog_handler
from slack.incident_commands import incident_command
from slack.slack_utils import user_reference

from django.conf import settings

PAGE_SPECIALIST_DIALOG = "page_specialist_dialog"
ESCALATE_BUTTON = "escalate_button_id"


def incident_key(incident):
    return f"monzo-incident-{incident.pk}"


# @action_handler(PAGE_ONCALL_ENGINEER_BUTTON)
# def headline_post_handle_page_oncall_engineer(incident: Incident, user_id: str, message: json, trigger_id: str, response_url: str, value: str):
#     key = incident_key(incident)
#     trigger_incident(incident.report, incident.summary or "", settings.PAGERDUTY_SERVICE, key)

#     user_ref = user_reference(user_id)
#     incident.post_to_thread(f":pager: Engineer paged by {user_ref}")


@incident_command(['escalate', 'esc'], helptext='Escalate to someone else')
def handle_escalatations(incident: Incident, user_id: str, message: str):
    # escalations = Escalation.objects.all()

    # if not escalations:
    #     msg = Message()
    #     msg.add_block(Section(text=Text("No specialists have been configured 😢")))
    # else:
    #     msg = Message()
    #     msg.add_block(Section(text=Text("Let's find the right people to help out 🔍")))
    #     msg.add_block(Divider())
    #     msg.add_block(Section(text=Text("These are the teams available as specialist escalations:")))

    #     for team in escalations:
    #         team_section = Section(
    #             text=Text(f"*{team.name}*\n{team.summary}"),
    #             accessory=Button(f"📟 Page {team.name}", ESCALATE_BUTTON, value=f"{team.name}")
    #         )
    #         msg.add_block(team_section)

    #     msg.add_block(Divider())
    #     msg.add_block(Section(text=Text("Not sure who to pick? The Primary On-callers can help!")))

    # msg.send(incident.comms_channel_id)

    return True


# @action_handler(ESCALATE_BUTTON)
# def handle_page_oncall_engineer(incident: Incident, user_id: str, message: json, trigger_id: str, response_url: str, specialist: str):
#     dialog = Dialog(
#         title="Escalate to a Specialist",
#         submit_label="Escalate",
#         elements=[
#             DialogText(label="Message", name="message", placeholder="Why do you need them?", hint="You might be waking this person up.  Please make this friendly and clear"),
#         ],
#         state=specialist
#     )

#     dialog.send_open_dialog(PAGE_SPECIALIST_DIALOG, trigger_id)
#     return True


# @dialog_handler(PAGE_SPECIALIST_DIALOG)
# def page_specialist_dialog(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
#     incident = Incident.objects.get(comms_channel_id=channel_id)
#     specialist = PagerDutySpecialist.objects.get(name=state)
#     message = submission['message']

#     page_specialist.after_response(incident, specialist, message)

#     return


# @after_response.enable
# def page_specialist(incident: Incident, specialist: PagerDutySpecialist, message: str):
#     # check if a pagerduty incident exists
#     key = incident_key(incident)
#     pd_incident = next(iter(pypd.Incident.find(incident_key=key)), None)

#     if pd_incident:
#         # existing pagerduty incident found so reassign to the specialists
#         from_user = pypd.User.find_one(email=settings.PAGERDUTY_EMAIL)
#         pd_incident.add_responders(settings.PAGERDUTY_EMAIL, from_user.id, message, escalation_policy_ids=[specialist.escalation_policy])
#     else:
#         # no existing pagerduty incident so trigger one directly for the specialists
#         trigger_incident(message, incident.summary, settings.PAGERDUTY_SERVICE, key, escalation_policy=specialist.escalation_policy)

#     incident.post_to_comms_channel(f"👋 Sit tight. I've escalated to the {specialist.name} team")
