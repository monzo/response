import re

from response.slack import cache


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
    user_profile = cache.get_user_profile(user_id)
    return "@" + user_profile["name"] or user_id


def slack_to_human_readable(value):
    # replace user references (<@U3231FFD>) with usernames (@chrisevans)
    value = re.sub(r"(<@U[A-Z0-9]+>)", user_ref_to_username, value)
    value = re.sub(r"(<#C[A-Z0-9]+\|([\-a-zA-Z0-9]+)>)", r"#\2", value)
    return value
