from core.models import Incident, Action, ExternalUser, Timeline
from slack.models import CommsChannel
from slack.decorators import incident_command, get_help
from slack.slack_utils import reference_to_id, get_user_profile, rename_channel, SlackError, GetOrCreateSlackExternalUser
from datetime import datetime

@incident_command(['help'], helptext='Display a list of commands and usage')
def send_help_text(incident: Incident, user_id: str, message: str):
    return True, get_help()


@incident_command(['summary'], helptext='Provide a summary of what\'s going on')
def update_summary(incident: Incident, user_id: str, message: str):
    incident.summary = message
    incident.save()

    user = GetOrCreateSlackExternalUser(external_id=user_id)
    Timeline.objects.new_event(incident=incident, author=user, source='slack_cmd_summary', text=message)
    return True, None


@incident_command(['impact'], helptext='Explain the impact of this')
def update_impact(incident: Incident, user_id: str, message: str):
    incident.impact = message
    incident.save()

    user = GetOrCreateSlackExternalUser(external_id=user_id)
    Timeline.objects.new_event(incident=incident, author=user, source='slack_cmd_impact', text=message)
    return True, None


@incident_command(['lead'], helptext='Assign someone as the incident lead')
def set_incident_lead(incident: Incident, user_id: str, message: str):
    assignee = reference_to_id(message) or user_id
    lead = GetOrCreateSlackExternalUser(external_id=assignee)
    incident.lead = lead
    incident.save()

    user = GetOrCreateSlackExternalUser(external_id=user_id)
    Timeline.objects.new_event(incident=incident, author=user, source='slack_cmd_lead', text=f'lead set to {lead.display_name}')
    return True, None


@incident_command(['severity', 'sev'], helptext='Set the incident severity')
def set_severity(incident: Incident, user_id: str, message: str):
    for sev_id, sev_name in Incident.SEVERITIES:
        # look for sev name (e.g. critical) or sev id (1)
        if (sev_name in message) or (sev_id in message):
            incident.severity = sev_id
            incident.save()
            return True, None

    user = GetOrCreateSlackExternalUser(external_id=user_id)
    Timeline.objects.new_event(incident=incident, author=user, source='slack_cmd_severity', text=message)
    return False, None


@incident_command(['rename'], helptext='Rename the incident channel')
def rename_incident(incident: Incident, user_id: str, message: str):
    try:
        comms_channel = CommsChannel.objects.get(incident=incident)
        comms_channel.rename(message)
        user = GetOrCreateSlackExternalUser(external_id=user_id)
        Timeline.objects.new_event(incident=incident, author=user, source='slack_cmd_rename', text=message)
    except SlackError:
        return True, "👋 Sorry, the channel couldn't be renamed. Make sure that name isn't taken already."
    return True, None


@incident_command(['duration'], helptext='How long has this incident been running?')
def set_severity(incident: Incident, user_id: str, message: str):
    duration = incident.duration()

    comms_channel = CommsChannel.objects.get(incident=incident)
    comms_channel.post_in_channel(f"The incident has been running for {duration}")

    return True, None


@incident_command(['close'], helptext='Close this incident.')
def close_incident(incident: Incident, user_id: str, message: str):
    comms_channel = CommsChannel.objects.get(incident=incident)

    if incident.is_closed():
        comms_channel.post_in_channel(f"This incident was already closed at {incident.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        return True, None

    incident.end_time = datetime.now()
    incident.save()

    comms_channel.post_in_channel(f"This incident has been closed! 📖 -> 📕")

    return True, None


@incident_command(['action'], helptext='Log a follow up action')
def set_action(incident: Incident, user_id: str, message: str):
    comms_channel = CommsChannel.objects.get(incident=incident)
    action_reporter = GetOrCreateSlackExternalUser(external_id=user_id)
    Action(incident=incident, details=message, user=action_reporter).save()
    return True, None
