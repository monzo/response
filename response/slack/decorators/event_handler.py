import logging
from collections import defaultdict

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned

from response.core.models.incident import Incident
from response.slack.models import CommsChannel


logger = logging.getLogger(__name__)

# Stores a map from slack event name to a list of callback functions
EVENT_MAPPINGS = defaultdict(list)


def slack_event(event, func=None):
    '''
    @slack_event is a decorator which registers a function as a handler
    for a particular slack_event (e.g. app_mention, pin_added, etc.)

    Arguments:
        event: Command to invoke this on

    Example usage:

    @slack_event('pin_added')
    def handle_pin_added(event_payload):
        do_some_stuff()
    '''
    def _wrapper(fn):
        EVENT_MAPPINGS[event].append(fn)
        return fn
    if func:
        return _wrapper(func)
    return _wrapper


def handle_event(payload):
    """
    Handles slack event callbacks and routes the action to the correct event handler

    @param payload the Slack event JSON payload
    """

    # the actual event is nested inside the 'event' key of the payload
    event = payload.get('event', '')
    event_type = event.get('type', '')

    # ignore bot messages
    if event.get('subtype', None) == 'bot_message':
        return

    # if it doesn't exist, error and return
    if event_type not in EVENT_MAPPINGS:
        logger.error(f"No handler found for event <{event_type}>")
        return

    # events use either channel_id _or_ channel as the key (thanks Slack)
    if 'channel_id' in event:
        channel_id = event['channel_id']
    elif 'channel' in event:
        channel_id = event['channel']
    else:
        channel_id = None

    # get the incident by the comms_channel_id
    try:
        comms_channel = CommsChannel.objects.get(channel_id=channel_id)
        incident = comms_channel.incident
    except CommsChannel.DoesNotExist:
        logger.error(f"Can't find incident associated with channel_id {channel_id}")
        return

    # call the registered handler
    for handler in EVENT_MAPPINGS[event_type]:
        handler(incident, payload['event'])
