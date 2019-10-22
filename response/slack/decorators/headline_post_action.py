import logging

logger = logging.getLogger(__name__)


SLACK_HEADLINE_POST_ACTION_MAPPINGS = {}


def headline_post_action(order=0, func=None):
    """headline_post_action

    Decorator that allows adding a button/action into the headline post. Should be attached
    to functions that take a HeadlinePost and return a Slack Action type (e.g. Button).

    Actions can be conditional - returning None means that no Action will be added.

    The order parameter determines the relative position the action appears in the post -
    actions will be ordered low-high from left to right. Actions with the same order number
    will be added in the order the decorator is executed, which depends on the order of file imports.

    Usage:
    @headline_post_action(100)
    def edit_incident(headline_post):
        return slack.block_kit.Button(":pencil2: Edit", EDIT_INCIDENT_BUTTON, value=headline_post.incident.pk)

    """

    def _wrapper(fn):
        SLACK_HEADLINE_POST_ACTION_MAPPINGS[
            order
        ] = SLACK_HEADLINE_POST_ACTION_MAPPINGS.get(order, []) + [fn]
        return fn

    if func:
        return _wrapper(func)

    return _wrapper
