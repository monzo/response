from response.core.models import Incident
from response.slack.models import CommsChannel
from response.slack .decorators import recurring_notification, single_notification


@recurring_notification(interval_mins=5, max_notifications=5)
def remind_severity(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.severity:
            comms_channel.post_in_channel("🌤️ This incident doesn't have a severity.  Please set one with `@incident severity ...`")
    except CommsChannel.DoesNotExist:
        pass


@recurring_notification(interval_mins=2, max_notifications=5)
def remind_incident_lead(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.lead:
            comms_channel.post_in_channel("👩‍🚒 This incident hasn't got a lead.  Please set one with `@incident lead ...`")
    except CommsChannel.DoesNotExist:
        pass

@recurring_notification(interval_mins=720, max_notifications=6)
def remind_close_incident(incident: Incident):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        if not incident.is_closed():
            comms_channel.post_in_channel(":timer_clock: This incident has been running a long time.  Can it be closed now?  Remember to pin important messages in order to create the timeline.")
    except CommsChannel.DoesNotExist:
        pass