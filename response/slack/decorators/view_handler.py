import logging
import after_response

logger = logging.getLogger(__name__)

VIEW_HANDLERS = {}


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

    view_submission = {}
    for _, block in payload["view"]["state"]["values"].items():
        for action_id, action in block.items():
            action_type = action["type"]

            if action_type == "plain_text_input":
                if "value" in action:
                    value = action["value"]
                else:
                    value = None
            elif action_type == "static_select":
                value = action["selected_option"]["value"]
            else:
                continue

            view_submission[action_id] = value
            
    handler(payload["trigger_id"], payload["user"]["id"], view_submission)
