from core.models.incident import Incident
from slack.models import CommsChannel

import logging
logger = logging.getLogger(__name__)

KEYWORD_HANDLERS = {}


def keyword_handler(keywords):
    def _wrapper(fn):
        for keyword in keywords:
            KEYWORD_HANDLERS[keyword] = fn
        return fn
    return _wrapper


def handle_keywords(payload):
    text = payload.get('text', '')
    user = payload.get('user', '')
    ts = payload.get('ts', '')
    channel = payload.get('channel', '')

    comms_channel = CommsChannel(channel_id=channel)

    for keyword, handler in KEYWORD_HANDLERS.items():
        if keyword.lower() in text.lower():
            handler(comms_channel, user, text, ts)
