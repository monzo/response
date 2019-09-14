from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def response_setting(name):
    if not name.startswith("RESPONSE_"):
        raise ValueError(
            "This template tag only supports getting settings for the response "
            "app, as accessing settings from templates is not secure by "
            "default."
        )
    return getattr(settings, name, None)
