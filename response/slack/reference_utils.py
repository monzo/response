import re


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