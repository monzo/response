from datetime import datetime

from response.core.models import Incident
from response.slack.decorators import recurring_notification
from response.slack.models import CommsChannel


@recurring_notification(interval_mins=5, max_notifications=5)
def remind_severity(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.severity:
            comms_channel.post_in_channel(
                "🌤️ This incident doesn't have a severity. Please set one with `@incident severity ...`"
            )
    except CommsChannel.DoesNotExist:
        pass


@recurring_notification(interval_mins=2, max_notifications=5)
def remind_incident_lead(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.lead:
            comms_channel.post_in_channel(
                "👩‍🚒 This incident hasn't got a lead. Please set one with `@incident lead ...`"
            )
    except CommsChannel.DoesNotExist:
        pass


@recurring_notification(interval_mins=1440, max_notifications=5)
def remind_close_incident(incident: Incident):

    # Only remind on weekdays (weekday returns an ordinal indexed from 0 on Monday)
    if datetime.now().weekday() in (5, 6):
        return

    # Only remind during the day to prevent alerting people at unsociable hours
    if datetime.now().hour not in range(9, 18):
        return

    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.is_closed():
            user_to_notify = incident.lead or incident.reporter
            comms_channel.post_in_channel(
                f":timer_clock: <@{user_to_notify.external_id}>, this incident has been running a long time."
                " Can it be closed now? Remember to pin important messages in order to create the timeline."
            )
    except CommsChannel.DoesNotExist:
        pass
