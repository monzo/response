import re

from django.conf import settings


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