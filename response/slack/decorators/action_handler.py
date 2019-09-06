import logging

import after_response

from response.core.models.incident import Incident
from response.slack.models.comms_channel import CommsChannel

logger = logging.getLogger(__name__)

SLACK_ACTION_MAPPINGS = {}


class ActionContext:
    def __init__(
        self, incident, user_id, message, button_value, trigger_id, response_url
    ):
        self.incident = incident
        self.user_id = user_id
        self.message = message
        self.button_value = button_value
        self.trigger_id = trigger_id
        self.response_url = response_url


def action_handler(callback_id, func=None):
    def _wrapper(fn):
        SLACK_ACTION_MAPPINGS[callback_id] = fn
        return fn

    if func:
        return _wrapper(func)
    return _wrapper


def remove_action_handler(callback_id):
    SLACK_ACTION_MAPPINGS.pop(callback_id, None)


@after_response.enable
def handle_action(payload):
    actions = payload["actions"]
    if actions:
        action_id = actions[0]["action_id"]

        if action_id not in SLACK_ACTION_MAPPINGS:
            logger.error(f"Can't find handler for action id {action_id}")
            return

        handler = SLACK_ACTION_MAPPINGS[action_id]

        user_id = payload["user"]["id"]
        channel_id = payload["channel"]["id"]
        button_value = actions[0]["value"]
        message = payload["message"]
        trigger_id = payload["trigger_id"]
        response_url = payload["response_url"]

        # we want to tie all actions to an incident, and have two ways to do this:
        # - if action comes from a comms channel, lookup the incident by comms channel id
        # - if not in comms channel, we rely on the button value containing the incident id
        try:
            comms_channel = CommsChannel.objects.get(channel_id=channel_id)
            incident = comms_channel.incident
        except CommsChannel.DoesNotExist:
            incident_id = button_value
            incident = Incident.objects.get(pk=incident_id)
        except Incident.DoesNotExist:
            logger.error(
                f"Can't find incident associated with channel {channel_id} or with id {incident_id}"
            )
            return

        action_context = ActionContext(
            incident=incident,
            user_id=user_id,
            message=message,
            button_value=button_value,
            trigger_id=trigger_id,
            response_url=response_url,
        )

        handler(action_context)
