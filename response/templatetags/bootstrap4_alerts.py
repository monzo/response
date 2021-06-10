from django import template

register = template.Library()


@register.filter
def bootstrap4_alert_class(message):
    if message.tags == "error":
        return "alert-danger"
    return f"alert-{message.tags}"
