import json
import logging

import after_response

logger = logging.getLogger(__name__)

VIEW_HANDLERS = {}


class ViewContext:
    def __init__(
        self, form_data, private_metadata, user_id, trigger_id, view_id, response_url
    ):
        self.form_data = form_data
        self.private_metadata = private_metadata
        self.user_id = user_id
        self.trigger_id = trigger_id
        self.view_id = view_id
        self.response_url = response_url


def view_handler(callback_id, func=None):
    def _wrapper(fn):
        VIEW_HANDLERS[callback_id] = fn
        return fn

    if func:
        return _wrapper(func)
    return _wrapper


@after_response.enable
def handle_view(payload):
    callback_id = payload["view"]["callback_id"]

    if callback_id not in VIEW_HANDLERS:
        logger.error(f"Can't find handler for callback id {callback_id}")
        return

    handler = VIEW_HANDLERS[callback_id]

    # Extract form data from view
    form_data = {}
    for _, block in payload["view"]["state"]["values"].items():
        for action_id, action in block.items():
            action_type = action["type"]

            if action_type == "plain_text_input":
                if "value" in action:
                    value = action["value"]
                else:
                    value = None
            elif action_type == "static_select":
                value = (
                    action["selected_option"]["value"]
                    if "selected_option" in action
                    else None
                )
            elif action_type == "users_select":
                value = action.get("selected_user", None)
            else:
                logger.error(f"Unknown action type {action_type}: {action}")
                continue

            form_data[action_id] = value

    # Extract any private metadata
    private_metadata = json.loads(payload["view"]["private_metadata"])

    view_context = ViewContext(
        form_data,
        private_metadata,
        payload["user"]["id"],
        payload["trigger_id"],
        payload["view"]["id"],
        payload["response_urls"],
    )
    handler(view_context)
