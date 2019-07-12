import logging

from response.core.models import Incident
from response.slack.models import CommsChannel
from response.slack.slack_utils import add_reaction, remove_reaction, send_ephemeral_message, send_message, SlackError

logger = logging.getLogger(__name__)

COMMAND_MAPPINGS = {}
COMMAND_HELP = {}


def get_help():
    '''
    get_help returns the help string for a command
    '''
    rendered = ''
    for k in sorted(COMMAND_HELP.keys()):
        rendered += f'`{k}` -  {COMMAND_HELP[k]}\n'
    return rendered


def get_commands():
    return COMMAND_MAPPINGS.keys()


def incident_command(commands: list, func=None, helptext=""):
    """
    @incident_command is a decorator which registers a function as a handler
    for a set of command strings

    Arguments:
        commands: A list of strings to register as commands
        helptext: Text to be displayed when the "help" command is run

    Example usage:

    @incident_command('lead', helptext='Set the incident lead')
    def handle_incident_lead(context):
        do_some_stuff()
    """
    def _wrapper(fn):
        for command in commands:
            COMMAND_MAPPINGS[command] = fn

        COMMAND_HELP[', '.join(commands)] = helptext

        return fn
    if func:
        return _wrapper(func)
    return _wrapper

def remove_incident_command(commands: list):
    for command in commands:
        COMMAND_MAPPINGS.pop(command, None)
        COMMAND_HELP.pop(', '.join(commands), None)


def handle_incident_command(command_name, message, thread_ts, channel_id, user_id):
    """
    Handler for app mention events of the format @<bot> <command> <extra text>

    @param payload an app mention string of the form @incident summary Something's happened
    """
    if command_name not in COMMAND_MAPPINGS:
        send_ephemeral_message(
            channel_id,
            user_id,
            "I'm sorry, I don't know how to help with that :grimacing:",
        )

        react_not_ok(channel_id, thread_ts)

        logger.error(f"No handler found for command {command_name}")
        return

    command = COMMAND_MAPPINGS[command_name]

    try:
        comms_channel = CommsChannel.objects.get(channel_id=channel_id)
        handled, response = command(comms_channel.incident, user_id, message)

        if handled:
            react_ok(channel_id, thread_ts)
        else:
            react_not_ok(channel_id, thread_ts)

        if response:
            send_message(comms_channel.channel_id, response)

    except CommsChannel.DoesNotExist:
        logger.error('No matching incident found for this channel')


def react_not_ok(channel_id, thread_ts):
    try:
        remove_reaction('white_check_mark', channel_id, thread_ts)
    except SlackError:
        pass

    try:
        add_reaction('question', channel_id, thread_ts)
    except SlackError:
        pass


def react_ok(channel_id, thread_ts):
    try:
        remove_reaction('question', channel_id, thread_ts)
    except SlackError:
        pass

    try:
        add_reaction('white_check_mark', channel_id, thread_ts)
    except SlackError:
        pass
