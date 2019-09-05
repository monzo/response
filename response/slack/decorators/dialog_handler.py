import logging

import after_response

logger = logging.getLogger(__name__)

DIALOG_HANDLERS = {}


def dialog_handler(callback_id, func=None):
    def _wrapper(fn):
        DIALOG_HANDLERS[callback_id] = fn

    if func:
        return _wrapper(func)
    return _wrapper


def remove_dialog_handler(callback_id):
    DIALOG_HANDLERS.pop(callback_id, None)


@after_response.enable
def handle_dialog(payload):
    callback_id = payload["callback_id"]
    if callback_id not in DIALOG_HANDLERS:
        logger.error(f"Can't find handler for dialog id {callback_id}")
        return

    callback = DIALOG_HANDLERS[callback_id]

    user_id = payload["user"]["id"]
    channel_id = payload["channel"]["id"]
    submission = payload["submission"]
    response_url = payload["response_url"]
    state = payload["state"]

    callback(user_id, channel_id, submission, response_url, state)
