import pypd

from django.conf import settings

if settings.PAGERDUTY_ENABLED:
    pypd.api_key = settings.PAGERDUTY_API_KEY


def trigger_incident(title, key, details=None, from_email=None, escalation_policy=None):
    data = {
        'type': 'incident',
        'title': title,
        'incident_key': key,
        'service': {
                'type': 'service_reference',
                'id': settings.PAGERDUTY_SERVICE,
        },
        'body': {
            'type': 'incident_body',
            'details': details or "",
        },
        'urgency': 'high',
    }

    if escalation_policy:
        data['escalation_policy'] = {
            "id": escalation_policy,
            "type": "escalation_policy_reference"
        }

    pypd.Incident.create(
        data=data,
        add_headers={'from': from_email or settings.PAGERDUTY_DEFAULT_EMAIL}
    )
