import logging

import slackclient

logger = logging.getLogger(__name__)

class SlackError(Exception):
    pass

class SlackClient(object):
    def __init__(self, api_token):
        self.api_token = api_token
        self.client = slackclient.SlackClient(self.api_token)

    def api_call(self, api_endpoint, *args, **kwargs):
        logger.info(f"Calling Slack API {api_endpoint}")
        response = self.client.api_call(api_endpoint, *args, **kwargs)
        if not response.get("ok", False):
            error = response.get("error", "<no error given>")
            raise SlackError(f"Error calling Slack API endpoint '{api_endpoint}': {error}")
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


