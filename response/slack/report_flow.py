from datetime import datetime

from response.slack import block_kit
from response.slack.decorators.view_handler import view_handler, ViewContext
from response.core.models import ExternalUser, Incident
from response.slack.cache import get_user_profile
from response.slack.reference_utils import channel_reference


from django.conf import settings


def start_report_flow(user_id, channel_id, report, trigger_id):
    recent_incidents = True
    if recent_incidents:
        msg = block_kit.Message()

        if report:
            msg.add_block(
                block_kit.Section(
                    text=block_kit.Text(f"You're about to report:\n\n```{report}```")
                )
            )

        msg.add_block(
            block_kit.Section(
                text=block_kit.Text(
                    "The following incident has been declared recently:"
                )
            )
        )

        private_metadata = {"report": report, "channel_id": channel_id}

        msg.open_modal(
            trigger_id,
            "duplicate-checker",
            "Is this a duplicate?",
            "I need to report it",
            "Mine is a duplicate",
            private_metadata=private_metadata,
        )
    else:
        basic_report_capture(user_id, channel_id, report, trigger_id)


@view_handler("duplicate-checker")
def duplicate_checker(vc: ViewContext):
    report = vc.private_metadata["report"] if "report" in vc.private_metadata else None
    channel_id = vc.private_metadata["channel_id"]
    basic_report_capture(vc.user_id, channel_id, report, vc.trigger_id)


def basic_report_capture(user_id, channel_id, report, trigger_id):
    msg = block_kit.Message()

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
            multiline=True,
            optional=True,
        )
    )

    msg.open_modal(
        trigger_id,
        "basic_report_capture",
        "Report an Incident",
        "Report",
        "Cancel",
        private_metadata={"channel_id": channel_id},
    )


@view_handler("basic_report_capture")
def basic_report_capture_submit(vc: ViewContext):
    user_id = vc.user_id
    channel_id = vc.private_metadata["channel_id"]
    report = vc.form_data["report"]
    trigger_id = vc.trigger_id

    # Fork into the report only flow here
    if "report_only" in vc.form_data and vc.form_data["report_only"] == "true":
        report_only_capture(user_id, channel_id, report, trigger_id)
        return

    name = get_user_profile(user_id)["name"]
    reporter, _ = ExternalUser.objects.get_or_create_slack(
        external_id=vc.user_id, display_name=name
    )

    Incident.objects.create_incident(
        report=report,
        reporter=reporter,
        report_time=datetime.now(),
        report_only=False,
        summary=vc.form_data["summary"],
        impact=vc.form_data["impact"],
    )

    incidents_channel_ref = channel_reference(settings.INCIDENT_CHANNEL_ID)

    text = (
        f"Thanks for raising the incident 🙏\n\nHead over to {incidents_channel_ref} "
        "help deal with the issue"
    )

    settings.SLACK_CLIENT.send_ephemeral_message(channel_id, vc.user_id, text)


def report_only_capture(user_id, channel_id, report, trigger_id):
    msg = block_kit.Message()

    msg.add_block(
        block_kit.PlainTextInput(
            label="Report",
            placeholder_text="What's the tl;dr?",
            initial_value=report,
            action_id="report",
            block_id="report",
        )
    )

    msg.add_block(
        block_kit.PlainTextInput(
            label="Summary",
            action_id="summary",
            block_id="summary",
            placeholder_text="Can you share any more details?",
            multiline=True,
        )
    )

    msg.add_block(block_kit.Context("This should fully explain what's happened"))

    msg.add_block(
        block_kit.PlainTextInput(
            label="Impact",
            action_id="impact",
            block_id="impact",
            placeholder_text="Who or what might be affected?",
            multiline=True,
        )
    )

    msg.add_block(
        block_kit.Context(
            "This should detail any impacted processes, people, or systems"
        )
    )

    msg.add_block(
        block_kit.StaticSelectInput(
            options=[
                block_kit.StaticSelectOption(sev.capitalize(), i)
                for i, sev in Incident.SEVERITIES
            ],
            label="Severity",
            action_id="severity",
            block_id="severity",
        )
    )

    msg.open_modal(
        trigger_id,
        "report_only_capture",
        "Report an Incident",
        "Report",
        "Cancel",
        private_metadata={"channel_id": channel_id},
    )


@view_handler("report_only_capture")
def report_only_capture_submit(vc: ViewContext):
    user_id = vc.user_id
    channel_id = vc.private_metadata["channel_id"]
    report = vc.form_data["report"]
    time_now = datetime.now()

    name = get_user_profile(user_id)["name"]
    reporter, _ = ExternalUser.objects.get_or_create_slack(
        external_id=vc.user_id, display_name=name
    )

    Incident.objects.create_incident(
        report=report,
        reporter=reporter,
        lead=reporter,
        report_time=time_now,
        start_time=time_now,
        end_time=time_now,
        report_only=True,
        summary=vc.form_data["summary"],
        impact=vc.form_data["impact"],
        severity=vc.form_data["severity"],
    )

    incidents_channel_ref = channel_reference(settings.INCIDENT_REPORT_CHANNEL_ID)

    text = (
        f"Thanks for reporting the incident 🙏\n\nHead over to {incidents_channel_ref} "
        f"if you need to make any changes."
    )

    settings.SLACK_CLIENT.send_ephemeral_message(channel_id, vc.user_id, text)
