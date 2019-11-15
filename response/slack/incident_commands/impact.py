import json
import logging

from response.core.models import Incident
from response.slack import block_kit, dialog_builder
from response.slack.decorators import ActionContext, action_handler, dialog_handler
from response.slack.decorators.incident_command import __default_incident_command
from response.slack.models import CommsChannel

logger = logging.getLogger(__name__)

UPDATE_CURRENT_IMPACT_ACTION = "update-current-impact-action"
SET_NEW_IMPACT_ACTION = "set-new-impact-action"
PROPOSED_MESSAGE_BLOCK_ID = "proposed"
UPDATE_IMPACT_DIALOG = "update-impact-dialog"

NO_IMPACT_TEXT = "The impact of this incident hasn't been set yet."
CURRENT_TITLE = "*This is the current impact:*\n"
PROPOSED_TITLE = "*Or would you like to update the impact to this?*\n"
IMPACT_UPDATED_TITLE = "*The impact has been updated to:*\n"
CHANGE_BUTTON_TEXT = "Change"
ACCEPT_PROPOSED_TEXT = "Yes"


@__default_incident_command(["impact"], helptext="Explain the impact of this")
def update_impact(incident: Incident, user_id: str, message: str):
    # Easy case. No impact currently and one has been provided
    if message and not incident.impact:
        incident.impact = message
        incident.save()
        return True, f"{IMPACT_UPDATED_TITLE}{message}"

    # Either no new impact has been provided, or one already exists
    msg = block_kit.Message()
    msg.add_block(
        block_kit.Section(
            block_id="update",
            text=block_kit.Text(f"{CURRENT_TITLE}{incident.impact or NO_IMPACT_TEXT}"),
            accessory=block_kit.Button(
                CHANGE_BUTTON_TEXT, UPDATE_CURRENT_IMPACT_ACTION, value=incident.pk
            ),
        )
    )

    # if the user has supplied a message, provide the option for them to set it without
    # retyping in the dialog
    if message:
        msg.add_block(
            block_kit.Section(
                block_id=PROPOSED_MESSAGE_BLOCK_ID,
                text=block_kit.Text(f"{PROPOSED_TITLE}{message}"),
                accessory=block_kit.Button(
                    ACCEPT_PROPOSED_TEXT, SET_NEW_IMPACT_ACTION, value=incident.pk
                ),
            )
        )

    comms_channel = CommsChannel.objects.get(incident=incident)
    msg.send(comms_channel.channel_id)
    return True, None


@action_handler(SET_NEW_IMPACT_ACTION)
def handle_set_new_impact(action_context: ActionContext):
    for block in action_context.message["blocks"]:
        print("Looking at block", block)
        if block["block_id"] == PROPOSED_MESSAGE_BLOCK_ID:
            impact = block["text"]["text"].replace(PROPOSED_TITLE, "")
            action_context.incident.impact = impact
            action_context.incident.save()

            comms_channel = CommsChannel.objects.get(incident=action_context.incident)
            comms_channel.post_in_channel(f"{IMPACT_UPDATED_TITLE}{impact}")
            return


@action_handler(UPDATE_CURRENT_IMPACT_ACTION)
def handle_open_impact_dialog(action_context: ActionContext):
    dialog = dialog_builder.Dialog(
        title="Update Impact",
        submit_label="Update",
        state=action_context.incident.pk,
        elements=[
            dialog_builder.TextArea(
                label="Impact",
                name="impact",
                optional=False,
                value=action_context.incident.impact,
            )
        ],
    )

    dialog.send_open_dialog(UPDATE_IMPACT_DIALOG, action_context.trigger_id)


@dialog_handler(UPDATE_IMPACT_DIALOG)
def update_status_page(
    user_id: str, channel_id: str, submission: json, response_url: str, state: json
):
    incident_id = state
    incident = Incident.objects.get(pk=incident_id)
    incident.impact = submission["impact"]
    incident.save()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f'{IMPACT_UPDATED_TITLE}{submission["impact"]}')
