import logging

from django.conf import settings

from response.slack.client import SlackError
from response.slack.models.comms_channel import CommsChannel

logger = logging.getLogger(__name__)

COMMAND_MAPPINGS = {}
COMMAND_MAPPINGS_CUSTOM = {}
COMMAND_HELP = {}


def get_help():
    """
    get_help returns the help string for a command
    """
    rendered = ""
    for k in sorted(COMMAND_HELP.keys()):
        rendered += f"`{k}` -  {COMMAND_HELP[k]}\n"
    return rendered


def get_commands():
    return COMMAND_MAPPINGS.keys()


def __default_incident_command(commands: list, func=None, helptext=""):
    """
    @__default_incident_command is a decorator which registers a function as
    the default handler for a set of command strings

    Arguments:
        commands: A list of strings to register as commands
        helptext: Text to be displayed when the "help" command is run

    Example usage:

    @__default_incident_command('lead', helptext='Set the incident lead')
    def handle_incident_lead(context):
        do_some_stuff()
    """

    def _wrapper(fn):
        for command in commands:
            COMMAND_MAPPINGS[command] = fn

        COMMAND_HELP[", ".join(commands)] = helptext

        return fn

    if func:
        return _wrapper(func)
    return _wrapper


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
            COMMAND_MAPPINGS_CUSTOM[command] = fn

        COMMAND_HELP[", ".join(commands)] = helptext

        return fn

    if func:
        return _wrapper(func)
    return _wrapper


def handle_incident_command(command_name, message, thread_ts, channel_id, user_id):
    """
    Handler for app mention events of the format @<bot> <command> <extra text>

    @param payload an app mention string of the form @incident summary Something's happened
    """
    if (
        command_name not in COMMAND_MAPPINGS
        and command_name not in COMMAND_MAPPINGS_CUSTOM
    ):
        settings.SLACK_CLIENT.send_ephemeral_message(
            channel_id,
            user_id,
            "I'm sorry, I don't know how to help with that :grimacing:",
        )

        react_not_ok(channel_id, thread_ts)

        logger.error(f"No handler found for command {command_name}")
        return

    if command_name in COMMAND_MAPPINGS_CUSTOM:
        logger.info(
            f"Handling incident command {command_name} '{message}' in channel {channel_id} with custom handler"
        )
        command = COMMAND_MAPPINGS_CUSTOM[command_name]
    else:
        logger.info(
            f"Handling incident command {command_name} '{message}' in channel {channel_id}"
        )
        command = COMMAND_MAPPINGS[command_name]

    try:
        comms_channel = CommsChannel.objects.get(channel_id=channel_id)
        handled, response = command(comms_channel.incident, user_id, message)

        if handled:
            react_ok(channel_id, thread_ts)
        else:
            react_not_ok(channel_id, thread_ts)

        if response:
            settings.SLACK_CLIENT.send_message(comms_channel.channel_id, response)

    except CommsChannel.DoesNotExist:
        logger.error("No matching incident found for this channel")
    except Exception as e:
        logger.error(f"Error handling incident command {command_name} {message}: {e}")
        raise


def react_not_ok(channel_id, thread_ts):
    try:
        settings.SLACK_CLIENT.remove_reaction("white_check_mark", channel_id, thread_ts)
    except SlackError as e:
        logger.error(
            f"Couldn't remove existing reaction from {channel_id} - {thread_ts}. Error: {e}"
        )

    try:
        settings.SLACK_CLIENT.add_reaction("question", channel_id, thread_ts)
    except SlackError as e:
        logger.error(
            f"Couldn't add 'question' reaction to {channel_id} - {thread_ts}. Error: {e}"
        )


def react_ok(channel_id, thread_ts):
    try:
        settings.SLACK_CLIENT.remove_reaction("question", channel_id, thread_ts)
    except SlackError as e:
        logger.error(
            f"Couldn't remove existing reaction from {channel_id} - {thread_ts}. Error: {e}"
        )

    try:
        settings.SLACK_CLIENT.add_reaction("white_check_mark", channel_id, thread_ts)
    except SlackError as e:
        logger.error(
            f"Couldn't add 'white_check_mark' reaction to {channel_id} - {thread_ts}. Error: {e}"
        )
