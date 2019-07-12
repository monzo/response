import json

from response.slack.workflows.statuspage.connections import get_status_page_conn

from response.slack.models import Incident
from response.core.models import IncidentExtension
from response.slack.slack_utils import send_ephemeral_message


def handle_status_page_update(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    incident_id = state
    incident = Incident.objects.get(pk=incident_id)
    statuspage_incident_id, created = IncidentExtension.objects.get_or_create(incident=incident, key='statuspage_incident_id')

    vars = {
        'name': submission['name'],
        'status': submission['incident_status'],
        'message': submission['message'] or '',
        'impact_override': submission['impact_override'] or '',
        'wants_twitter_update': bool(submission.get('wants_twitter_update', "False") == "True"),
    }
    try:
        if statuspage_incident_id.value:
            get_status_page_conn().incidents.update(incident_id=statuspage_incident_id.value, **vars)
        else:
            response = get_status_page_conn().incidents.create(**vars)
            statuspage_incident_id.value = response['id']
            statuspage_incident_id.save()

        msg = f'The status page has been updated 👍'

    except Exception as ex:
        msg = f'⚠️ {repr(ex)}'

    send_ephemeral_message(channel_id, user_id, msg)
