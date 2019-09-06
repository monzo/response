import logging

import emoji_data_python
from django import template
from django.conf import settings

from response.slack.client import slack_to_human_readable

register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def unslackify(value):
    """Takes a string and turns slack style :emoji: into unicode"""

    value = slack_to_human_readable(value)

    # replace all colon style :emoji: with unicode
    value = emoji_data_python.replace_colons(value)

    return value


@register.filter
def slack_id_to_fullname(value):
    profile = settings.SLACK_CLIENT.get_user_profile(value)
    if profile:
        return profile["fullname"]
