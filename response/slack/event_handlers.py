import json
import logging
import re

from response.core.models.incident import Incident
from response.slack.decorators import (
    handle_incident_command,
    handle_keywords,
    slack_event,
)
from response.slack.models import CommsChannel, PinnedMessage, UserStats

logger = logging.getLogger(__name__)


def decode_app_mention(payload):
    """
    Convenience function for dealing with the common pattern for app mention slack events.

    Example: @bot create Something's happened
    Extracts:  slack_id -> "@bot"
               command  -> "create"
               extra    -> "Something's happened"

    @param payload an app mention string of the form @bot create Something's happened
    @return: three variables split by bot, action and extra text
    """
    incident_command_re = re.compile(r"(<@[A-Z0-9]+>)\s+(\w+)\s*(.*)")
    m = incident_command_re.match(payload.strip())

    if not m or len(m.groups()) != 3:
        raise ValueError(
            f'Could not parse app mention payload "{payload}" into "@<bot> <command> <text>"'
        )

    slack_id = m.group(1)
    command = m.group(2)
    extra = m.group(3)

    return slack_id, command, extra


@slack_event("app_mention")
def handle_app_mention(incident: Incident, payload: json):
    """
    Events of type `app_mention` are of the form `@incident some text here`
    We handle all of these as incident_commands
    """
    _, command_name, message = decode_app_mention(payload["text"])

    channel_id = payload["channel"]
    user_id = payload["user"]
    thread_ts = payload["ts"]

    handle_incident_command(command_name, message, thread_ts, channel_id, user_id)


@slack_event("message")
def handle_keyword_detection(incident: Incident, payload: json):
    handle_keywords(incident, payload)


@slack_event("message")
def update_user_stats(incident: Incident, payload: json):
    # message with a user field are messages coming from users.
    if "user" in payload:
        user_id = payload["user"]
        UserStats.increment_message_count(incident, user_id)


@slack_event("pin_added")
def handle_pin_added(incident, payload):
    """
    Handler for pin added events

    @param payload a slack pin_added event
    """
    pinned_message = payload["item"]["message"]

    if "user" in pinned_message:
        author_id = pinned_message["user"]
        message_ts = pinned_message["ts"]
        text = pinned_message["text"]
        PinnedMessage.objects.add_pin(incident, message_ts, author_id, text)


@slack_event("pin_removed")
def handle_pin_removed(incident, payload):
    """
    Handler for pin removed events

    @param payload a slack pin_removed event
    """

    pinned_message = payload["item"]["message"]
    message_ts = pinned_message["ts"]

    PinnedMessage.objects.remove_pin(incident, message_ts)


@slack_event("channel_rename")
def handle_channel_rename(incident, payload):
    new_name = payload["channel"]["name"]
    logger.info(f"Renaming channel: {id} to {new_name}")
    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.channel_name = new_name
    comms_channel.save()
