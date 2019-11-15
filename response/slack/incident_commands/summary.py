import json
import logging

from response.core.models import Incident
from response.slack import block_kit, dialog_builder
from response.slack.decorators import ActionContext, action_handler, dialog_handler
from response.slack.decorators.incident_command import __default_incident_command
from response.slack.models import CommsChannel

logger = logging.getLogger(__name__)

UPDATE_CURRENT_SUMMARY_ACTION = "update-current-summary-action"
SET_NEW_SUMMARY_ACTION = "set-new-summary-action"
PROPOSED_MESSAGE_BLOCK_ID = "proposed"
UPDATE_SUMMARY_DIALOG = "update-summary-dialog"

NO_SUMMARY_TEXT = "This incident doesn't have a summary yet."
CURRENT_TITLE = "*This is the current summary:*\n"
PROPOSED_TITLE = "*Or would you like to update the summary to this?*\n"
SUMMARY_UPDATED_TITLE = "*The summary has been updated to:*\n"
CHANGE_BUTTON_TEXT = "Change"
ACCEPT_PROPOSED_TEXT = "Yes"


@__default_incident_command(
    ["summary"], helptext="Provide a summary of what's going on"
)
def update_summary(incident: Incident, user_id: str, message: str):
    # Easy case. No summary currently and one has been provided
    if message and not incident.summary:
        incident.summary = message
        incident.save()
        return True, f"{SUMMARY_UPDATED_TITLE}{message}"

    # Either no new summary has been provided, or one already exists
    msg = block_kit.Message()

    msg.add_block(
        block_kit.Section(
            block_id="update",
            text=block_kit.Text(
                f"{CURRENT_TITLE}{incident.summary or NO_SUMMARY_TEXT}"
            ),
            accessory=block_kit.Button(
                CHANGE_BUTTON_TEXT, UPDATE_CURRENT_SUMMARY_ACTION, value=incident.pk
            ),
        )
    )

    # if the user has supplied a message, provide the option for them to set it without
    # retyping in the dialog
    if message:
        msg.add_block(block_kit.Divider())
        msg.add_block(
            block_kit.Section(
                block_id=PROPOSED_MESSAGE_BLOCK_ID,
                text=block_kit.Text(f"{PROPOSED_TITLE}{message}"),
                accessory=block_kit.Button(
                    ACCEPT_PROPOSED_TEXT, SET_NEW_SUMMARY_ACTION, value=incident.pk
                ),
            )
        )

    comms_channel = CommsChannel.objects.get(incident=incident)
    msg.send(comms_channel.channel_id)
    return True, None


@action_handler(SET_NEW_SUMMARY_ACTION)
def handle_set_new_summary(action_context: ActionContext):
    for block in action_context.message["blocks"]:
        print("Looking at block", block)
        if block["block_id"] == PROPOSED_MESSAGE_BLOCK_ID:
            summary = block["text"]["text"].replace(PROPOSED_TITLE, "")
            action_context.incident.summary = summary
            action_context.incident.save()

            comms_channel = CommsChannel.objects.get(incident=action_context.incident)
            comms_channel.post_in_channel(f"{SUMMARY_UPDATED_TITLE}{summary}")
            return


@action_handler(UPDATE_CURRENT_SUMMARY_ACTION)
def handle_open_summary_dialog(action_context: ActionContext):
    dialog = dialog_builder.Dialog(
        title="Update Summary",
        submit_label="Update",
        state=action_context.incident.pk,
        elements=[
            dialog_builder.TextArea(
                label="Summary",
                name="summary",
                optional=False,
                value=action_context.incident.summary,
            )
        ],
    )

    dialog.send_open_dialog(UPDATE_SUMMARY_DIALOG, action_context.trigger_id)


@dialog_handler(UPDATE_SUMMARY_DIALOG)
def update_status_page(
    user_id: str, channel_id: str, submission: json, response_url: str, state: json
):
    incident_id = state
    incident = Incident.objects.get(pk=incident_id)
    incident.summary = submission["summary"]
    incident.save()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f'{SUMMARY_UPDATED_TITLE}{submission["summary"]}')
