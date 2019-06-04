from core.models import Incident
from slack.models import CommsChannel
from slack.decorators import incident_command, get_help
from slack.slack_utils import reference_to_id, rename_channel, SlackError


@incident_command(['help'], helptext='Display a list of commands and usage')
def send_help_text(incident: Incident, user_id: str, message: str):
    return True, get_help()


@incident_command(['summary'], helptext='Provide a summary of what\'s going on')
def update_summary(incident: Incident, user_id: str, message: str):
    incident.summary = message
    incident.save()
    return True, None


@incident_command(['impact'], helptext='Explain the impact of this')
def update_impact(incident: Incident, user_id: str, message: str):
    incident.impact = message
    incident.save()
    return True, None


@incident_command(['lead'], helptext='Assign someone as the incident lead')
def set_incident_lead(incident: Incident, user_id: str, message: str):
    assignee = reference_to_id(message)
    incident.lead = assignee or user_id
    incident.save()
    return True, None


@incident_command(['severity', 'sev'], helptext='Set the incident severity')
def set_severity(incident: Incident, user_id: str, message: str):
    for sev_id, sev_name in Incident.SEVERITIES:
        # look for sev name (e.g. critical) or sev id (1)
        if (sev_name in message) or (sev_id in message):
            incident.severity = sev_id
            incident.save()
            return True, None

    return False, None


@incident_command(['rename'], helptext='Rename the incident channel')
def rename_incident(incident: Incident, user_id: str, message: str):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        comms_channel.rename(message)
    except SlackError:
        return True, "👋 Sorry, the channel couldn't be renamed. Make sure that name isn't taken already."
    return True, None


@incident_command(['duration'], helptext='How long has this incident been running?')
def set_severity(incident: Incident, user_id: str, message: str):
    duration = incident.duration()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f"The incident has been running for {duration}")

    return True, None

