import logging

import emoji_data_python
from django import template

from response.slack.cache import get_user_profile
from response.slack.reference_utils import slack_to_human_readable

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
    profile = get_user_profile(value)
    if profile:
        return profile["fullname"]
