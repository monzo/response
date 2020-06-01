import logging
import time

import slackclient
from slugify import slugify

logger = logging.getLogger(__name__)


class SlackError(Exception):
    def __init__(self, message, slack_error=None):
        self.message = message
        self.slack_error = slack_error


class SlackClient(object):
    def __init__(
        self,
        api_token,
        max_retry_attempts=10,
        retry_base_backoff_seconds=0.2,
        retryable_errors=None,
    ):
        self.api_token = api_token
        self.client = slackclient.SlackClient(self.api_token)
        self.max_retry_attempts = max_retry_attempts
        self.retry_base_backoff_seconds = retry_base_backoff_seconds
        self.retryable_errors = retryable_errors or ["ratelimited"]

    def api_call(self, api_endpoint, *args, **kwargs):
        logger.info(f"Calling Slack API {api_endpoint}")
        response = self.client.api_call(api_endpoint, *args, **kwargs)
        if not response.get("ok", False):
            error = response.get("error", "<no error given>")

            # Check if we want to back off and retry (but only if this isn't a
            # retry attempt itself)
            if error in self.retryable_errors and not kwargs.get("is_retrying", False):
                # Iterate over retry attempts. We could implement this
                # recursively, but there's a danger of overflowing the stack

                # Start index at 1 so we have a multiplier for backoff
                for i in range(1, self.max_retry_attempts + 1):
                    try:
                        # Increase backoff with every attempt
                        backoff_seconds = self.retry_base_backoff_seconds * i
                        logging.warning(
                            f"Retrying request to {api_endpoint} after error {error}. Backing off {backoff_seconds:.2f}s (attempt {i} of {self.max_retry_attempts})"
                        )

                        time.sleep(backoff_seconds)
                        return self.api_call(
                            api_endpoint, is_retrying=True, *args, **kwargs
                        )
                    except SlackError as exc:
                        if exc.slack_error not in self.retryable_errors:
                            raise exc

            raise SlackError(
                f"Error calling Slack API endpoint '{api_endpoint}': {error}",
                slack_error=error,
            )
        return response

    def users_list(self):
        logger.info("Listing Slack users")
        return self.api_call("users.list")

    def get_paginated_users(self, limit=0, cursor=None):
        response = self.api_call("users.list", limit=limit, cursor=cursor)
        return response

    def get_user_id(self, name):
        logger.info(f"Getting user ID for {name}")
        response = self.users_list()
        for user in response["members"]:
            if user["name"] == name:
                return user["id"]
        raise SlackError(f"User '{name}' not found")

    def get_channel_name(self, id_):
        try:
            response = self.api_call("conversations.info", channel=id_)
            return response["channel"]["name"]
        except SlackError as e:
            if e.slack_error == "channel_not_found":
                return None
            raise

    def get_channel_id(self, name, auto_unarchive=False):
        logger.info(f"Getting channel ID for {name}")
        next_cursor = None

        while next_cursor != "":
            response = self.api_call(
                "channels.list",
                exclude_archived=not auto_unarchive,
                exclude_members=True,
                limit=800,
                cursor=next_cursor,
            )

            # see if there's a next_cursor
            try:
                next_cursor = response["response_metadata"]["next_cursor"]
                logger.info(f"get_channel_id - next_cursor == [{next_cursor}]")
            except LookupError:
                logger.error(
                    "get_channel_id - I guess checking next_cursor in response object didn't work."
                )

            for channel in response["channels"]:
                if channel["name"] == name:
                    if channel["is_archived"] and auto_unarchive:
                        self.unarchive_channel(channel["id"])
                    return channel["id"]

        raise SlackError(f"Channel '{name}' not found")

    def get_usergroup_id(self, group_handle):
        response = self.api_call("usergroups.list")
        if not response.get("ok", False):
            raise SlackError(
                f"Failed to get usergroup with group handle {group_handle} : {response['error']}"
            )
        for group in response["usergroups"]:
            if group["handle"] == group_handle:
                return group["id"]
        return None

    def get_usergroup_users(self, group_id):
        response = self.api_call("usergroups.list", include_users=True)

        if not response.get("ok", False):
            raise SlackError(
                f"Failed to get users from usergroup with id {group_id} : {response['error']}"
            )
        for group in response["usergroups"]:
            if group["id"] == group_id:
                return group["users"]
        return None

    def create_channel(self, name):
        response = self.api_call("channels.create", name=name)
        try:
            return response["channel"]["id"]
        except KeyError:
            raise SlackError(
                "Got unexpected response from Slack API for channels.create - couldn't find channel.id key"
            )

    def get_or_create_channel(self, channel_name, auto_unarchive=False):
        try:
            return self.create_channel(channel_name)
        except SlackError as e:
            if e.slack_error != "name_taken":
                # some other error, let's propagate it upwards
                raise

            return self.get_channel_id(channel_name, auto_unarchive)

    def set_channel_topic(self, channel_id, channel_topic):
        return self.api_call(
            "channels.setTopic", channel=channel_id, topic=channel_topic
        )

    def unarchive_channel(self, channel_id):
        response = self.api_call("channels.unarchive", channel=channel_id)
        if not response.get("ok", False):
            raise SlackError(f"Couldn't unarchive channel {channel_id}")

    def send_message(self, channel_id, text, attachments=None, thread_ts=None):
        return self.api_call(
            "chat.postMessage",
            channel=channel_id,
            text=text,
            attachments=attachments,
            thread_ts=thread_ts,
        )

    def send_ephemeral_message(self, channel_id, user_id, text, attachments=None):
        return self.api_call(
            "chat.postEphemeral",
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
                "Got unexpected response from Slack API for auth.test - couldn't find user_id key"
            )

    def invite_user_to_channel(self, user_id, channel_id):
        return self.api_call("channels.invite", user=user_id, channel=channel_id)

    def join_channel(self, channel_id):
        return self.api_call("channels.join", name=channel_id)

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
            "email": response["user"]["profile"].get("email", None),
        }

    def get_user_profile_by_email(self, email):
        if not email:
            return None

        response = self.api_call("users.lookupByEmail", email=email)

        return {
            "id": response["user"]["id"],
            "name": response["user"]["name"],
            "fullname": response["user"]["profile"]["real_name"],
            "email": email,
        }

    def rename_channel(self, channel_id, new_name):
        prefix = ""
        if not (new_name.startswith("inc-") or new_name.startswith("#inc-")):
            prefix = "inc-"

        new_name = slugify(f"{prefix}{new_name}", max_length=80)

        return self.api_call("channels.rename", channel=channel_id, name=new_name)

    def dialog_open(self, dialog, trigger_id):
        return self.api_call("dialog.open", trigger_id=trigger_id, dialog=dialog)
