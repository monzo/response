import logging

from response.core.models.incident import Incident
from response.slack.models.comms_channel import CommsChannel

logger = logging.getLogger(__name__)

KEYWORD_HANDLERS = {}


def keyword_handler(keywords, func=None):
    def _wrapper(fn):
        for keyword in keywords:
            KEYWORD_HANDLERS[keyword] = fn
        return fn

    if func:
        return _wrapper(func)
    return _wrapper


def handle_keywords(incident: Incident, payload):
    text = payload.get("text", "")
    user = payload.get("user", "")
    ts = payload.get("ts", "")

    comms_channel = CommsChannel.objects.get(incident=incident)

    for keyword, handler in KEYWORD_HANDLERS.items():
        if keyword.lower() in text.lower():
            handler(comms_channel, user, keyword, text, ts)
