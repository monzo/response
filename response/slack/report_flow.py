from datetime import datetime

from response.slack import block_kit
from response.slack.decorators import view_handler
from response.core.models import ExternalUser, Incident
from response.slack.cache import get_user_profile
from response.slack.reference_utils import channel_reference


from django.conf import settings


def start_report(user_id, report, trigger_id):
    msg = block_kit.Message()
    recent_incidents = False
    if recent_incidents:
        msg.add_block(
            block_kit.Section(text=block_kit.Text("Here's some previous incidents"))
        )
        msg.add_block(block_kit.Divider())

    msg.add_block(
        block_kit.PlainTextInput(
            label="Report",
            placeholder_text="What's the tl;dr?",
            initial_value=report,
            action_id="report",
            block_id="report",
        )
    )

    if hasattr(settings, "INCIDENT_REPORT_CHANNEL_ID"):
        msg.add_block(
            block_kit.StaticSelectInput(
                options=[
                    block_kit.StaticSelectOption(
                        "Yes - It's live and I'm going to need a comms channel", "false"
                    ),
                    block_kit.StaticSelectOption(
                        "No - I can fill in the report right now", "true"
                    ),
                ],
                label="Is this a live incident?",
                action_id="report_only",
                block_id="report_only",
            )
        )

    msg.add_block(
        block_kit.PlainTextInput(
            label="Summary",
            action_id="summary",
            block_id="summary",
            placeholder_text="Can you share any more details?",
            multiline=True,
            optional=True,
        )
    )

    msg.add_block(
        block_kit.PlainTextInput(
            label="Impact",
            action_id="impact",
            block_id="impact",
            placeholder_text="Who or what might be affected?",
            multiline=False,
            optional=True,
        )
    )

    msg.add_block(
        block_kit.StaticSelectInput(
            options=[
                block_kit.StaticSelectOption("Critical", "critical"),
                block_kit.StaticSelectOption("Major", "major"),
                block_kit.StaticSelectOption("Minor", "minor"),
                block_kit.StaticSelectOption("Trivial", "trivial"),
            ],
            label="Severity",
            action_id="severity",
            block_id="severity"
        )
    )

    msg.open_modal(
        trigger_id, "report-incident", "Report an Incident", "Report", "Cancel"
    )


@view_handler("report-incident")
def report_submit(trigger_id, user_id, view_submission: list):
    if "report_only" in view_submission and view_submission["report_only"] == "true":
        report_only = True
    else:
        report_only = False

    name = get_user_profile(user_id)["name"]
    reporter, _ = ExternalUser.objects.get_or_create_slack(
        external_id=user_id, display_name=name
    )

    Incident.objects.create_incident(
        report=view_submission["report"],
        reporter=reporter,
        report_time=datetime.now(),
        report_only=report_only,
        summary=view_submission["summary"],
        impact=view_submission["impact"],
    )

    if report_only and hasattr(settings, "INCIDENT_REPORT_CHANNEL_ID"):
        incidents_channel_ref = channel_reference(settings.INCIDENT_REPORT_CHANNEL_ID)
    else:
        incidents_channel_ref = channel_reference(settings.INCIDENT_CHANNEL_ID)

    text = (
        f"Thanks for raising the incident 🙏\n\nHead over to {incidents_channel_ref} "
        f"to complete the report and/or help deal with the issue"
    )
    #TODO: Get the channel ID from somewhere
    #settings.SLACK_CLIENT.send_ephemeral_message(channel_id, user_id, text)    


