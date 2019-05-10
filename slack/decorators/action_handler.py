import after_response

from core.models.incident import Incident

import logging
logger = logging.getLogger(__name__)

SLACK_ACTION_MAPPINGS = {}


def action_handler(callback_id):
    def _wrapper(fn):
        SLACK_ACTION_MAPPINGS[callback_id] = fn
        return fn
    return _wrapper


@after_response.enable
def handle_action(payload):
    actions = payload['actions']
    if actions:
        action_id = actions[0]['action_id']

        if action_id not in SLACK_ACTION_MAPPINGS:
            logger.error(f"Can't find handler for action id {action_id}")
            return

        handler = SLACK_ACTION_MAPPINGS[action_id]

        user_id = payload['user']['id']
        incident_id = actions[0]['value']
        message = payload['message']
        trigger_id = payload['trigger_id']

        try:
            incident = Incident.objects.get(id=incident_id)
            handler(incident, user_id, message, trigger_id=trigger_id)
        except Incident.DoesNotExist:
            logger.error(f"Can't find incident {incident_id} associated with action {action_id}")
