from django.conf import settings
import logging
import re

import slackclient
from slugify import slugify


logger = logging.getLogger(__name__)


class SlackError(Exception):
    def __init__(self, message, slack_error=None):
        self.message = message
        self.slack_error = slack_error


class SlackClient(object):
    def __init__(self, api_token):
        self.api_token = api_token
        self.client = slackclient.SlackClient(self.api_token)

    def api_call(self, api_endpoint, *args, **kwargs):
        logger.info(f"Calling Slack API {api_endpoint}")
        response = self.client.api_call(api_endpoint, *args, **kwargs)
        if not response.get("ok", False):
            error = response.get("error", "<no error given>")
            raise SlackError(
                f"Error calling Slack API endpoint '{api_endpoint}': {error}",
                slack_error=error,
            )
        return response

    def users_list(self):
        logger.info(f"Listing Slack users")
        return self.api_call("users.list")

    def get_user_id(self, name):
        logger.info(f"Getting user ID for {name}")
        response = self.users_list()
        for user in response["members"]:
            if user["name"] == name:
                return user["id"]
        raise SlackError(f"User '{name}' not found")

    def get_channel_id(self, name):
        logger.info(f"Getting channel ID for {name}")
        next_cursor = None

        while next_cursor != "":
            response = self.api_call(
                "channels.list",
                exclude_archived=True,
                exclude_members=True,
                limit=800,
                cursor=next_cursor,
            )

            # see if there's a next_cursor
            try:
                next_cursor = response["response_metadata"]["next_cursor"]
                logger.info(f"get_channel_id - next_cursor == [{next_cursor}]")
            except:
                logger.error(
                    f"get_channel_id - I guess checking next_cursor in response object didn't work."
                )

            for channel in response["channels"]:
                if channel["name"] == name:
                    return channel["id"]

        raise SlackError(f"Channel '{name}' not found")

    def create_channel(self, name):
        response = self.api_call("channels.create", name=name)
        try:
            return response["channel"]["id"]
        except KeyError:
            raise SlackError(
                f"Got unexpected response from Slack API for channels.create - couldn't find channel.id key"
            )

    def get_or_create_channel(self, channel_name, auto_unarchive=False):
        try:
            return self.create_channel(channel_name)
        except SlackError as e:
            if e.slack_error != "name_taken":
                # some other error, let's propagate it upwards
                raise

            return self.get_channel_id(channel_name)

    def set_channel_topic(self, channel_id, channel_topic):
        return self.api_call(
            "channels.setTopic", channel=channel_id, topic=channel_topic
        )

    def unarchive_channel(self, channel_id):
        return self.api_call("channels.unarchive", channel=channel_id)

    def send_message(self, channel_id, text, attachments=None, thread_ts=None):
        return self.api_call(
            "chat.postMessage",
            as_user=False,
            channel=channel_id,
            text=text,
            attachments=attachments,
            thread_ts=thread_ts,
        )

    def send_ephemeral_message(self, channel_id, user_id, text, attachments=None):
        return self.api_call(
            "chat.postEphemeral",
            as_user=False,
            channel=channel_id,
            text=text,
            user=user_id,
            attachments=attachments,
        )

    def send_or_update_message_block(self, channel_id, blocks, fallback_text, ts=None):
        api_call = "chat.postMessage" if not ts else "chat.update"

        return self.api_call(
            api_call, text=fallback_text, channel=channel_id, ts=ts, blocks=blocks
        )

    def add_reaction(self, reaction, channel_id, thread_ts):
        try:
            return self.api_call(
                "reactions.add", name=reaction, channel=channel_id, timestamp=thread_ts
            )
        except SlackError as e:
            if e.slack_error != "already_reacted":
                raise

    def remove_reaction(self, reaction, channel_id, thread_ts):
        try:
            return self.api_call(
                "reactions.remove",
                name=reaction,
                channel=channel_id,
                timestamp=thread_ts,
            )
        except SlackError as e:
            if e.slack_error != "no_reaction":
                raise

    def get_slack_token_owner(self):
        """
        return the id of the user associated with the current slack token
        """
        try:
            return self.api_call("auth.test")["user_id"]
        except KeyError:
            raise SlackError(
                f"Got unexpected response from Slack API for auth.test - couldn't find user_id key"
            )

    def invite_user_to_channel(self, user_id, channel_id):
        return self.api_call("channels.invite", user=user_id, channel=channel_id)

    def leave_channel(self, channel_id):
        return self.api_call("channels.leave", channel=channel_id)

    def get_user_profile(self, user_id):
        if not user_id:
            return None

        response = self.api_call("users.info", user=user_id)

        return {
            "id": user_id,
            "name": response["user"]["name"],
            "fullname": response["user"]["profile"]["real_name"],
        }

    def rename_channel(self, channel_id, new_name):
        prefix = ""
        if not (new_name.startswith("inc-") or new_name.startswith("#inc-")):
            prefix = "inc-"

        new_name = slugify(f"{prefix}{new_name}", max_length=21)

        return self.api_call("channels.rename", channel=channel_id, name=new_name)

    def dialog_open(self, dialog, trigger_id):
        return self.api_call("dialog.open", trigger_id=trigger_id, dialog=dialog)


def channel_reference(channel_id):
    if channel_id is None:
        return None
    return f"<#{channel_id}>"


def user_reference(user_id):
    return f"<@{user_id}>"


def reference_to_id(value):
    """take a string containing <@U123ABCD> refs and extract first match"""
    m = re.search(r"<@(U[A-Z0-9]+)>", value)
    return m.group(1) if m else None


def user_ref_to_username(value):
    """takes a <@U123ABCD> style ref and returns an @username"""
    # strip the '<@' and '>'
    user_id = reference_to_id(value.group())
    user_profile = settings.SLACK_CLIENT.get_user_profile(user_id)
    return "@" + user_profile["name"] or user_id


def slack_to_human_readable(value):
    # replace user references (<@U3231FFD>) with usernames (@chrisevans)
    value = re.sub(r"(<@U[A-Z0-9]+>)", user_ref_to_username, value)
    value = re.sub(r"(<#C[A-Z0-9]+\|([\-a-zA-Z0-9]+)>)", r"#\2", value)
    return value
