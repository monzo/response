from datetime import datetime
import json

from django.conf import settings

from response.slack.settings import INCIDENT_EDIT_DIALOG, INCIDENT_REPORT_DIALOG
from response.core.models.incident import Incident
from response.slack.models import HeadlinePost, CommsChannel, ExternalUser, GetOrCreateSlackExternalUser
from response.slack.decorators import dialog_handler
from response.slack.client import channel_reference
from pdpyras import  PDClientError


import logging
logger = logging.getLogger(__name__)


@dialog_handler(INCIDENT_REPORT_DIALOG)
def report_incident(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    report = submission['report']
    summary = submission['summary']
    impact = submission['impact']
    lead_id = submission['lead']
    severity = submission['severity']
    pdschedule = submission['pdschedule']

    name = settings.SLACK_CLIENT.get_user_profile(user_id)['name']
    reporter = GetOrCreateSlackExternalUser(external_id=user_id, display_name=name)

    lead = None
    if lead_id:
        lead_name = settings.SLACK_CLIENT.get_user_profile(lead_id)['name']
        lead = GetOrCreateSlackExternalUser(external_id=lead_id, display_name=lead_name)

    Incident.objects.create_incident(
        report=report,
        reporter=reporter,
        report_time=datetime.now(),
        summary=summary,
        impact=impact,
        lead=lead,
        severity=severity,
        pdschedule=pdschedule,
    )

    try:
        if pdschedule:
            res = settings.PDSESSION.rpost('/incidents',json={
                'incident':{
                    'type': 'incident',
                    'title': report,
                    'service': {
                        'id': pdschedule,
                        'type': 'service_reference',
                    },
                    'body': {
                        'type': 'incident_body',
                        'details': summary if summary else "",
                    },
                }
            }, headers={'From': 'marcos@zeit.co'})

    except PDClientError as pce:
        logger.error(pce.response.json())


    incidents_channel_ref = channel_reference(settings.INCIDENT_CHANNEL_ID)
    text = f"Thanks for raising the incident 🙏\n\nHead over to {incidents_channel_ref} to complete the report and/or help deal with the issue"
    settings.SLACK_CLIENT.send_ephemeral_message(channel_id, user_id, text)


@dialog_handler(INCIDENT_EDIT_DIALOG)
def edit_incident(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    report = submission['report']
    summary = submission['summary']
    impact = submission['impact']
    lead_id = submission['lead']
    severity = submission['severity']
    pdschedule = submission['pdschedule']

    lead = None
    if lead_id:
        lead_name = settings.SLACK_CLIENT.get_user_profile(lead_id)['name']
        lead = GetOrCreateSlackExternalUser(external_id=lead_id, display_name=lead_name)

    try:
        incident = Incident.objects.get(pk=state)

        prev_schedule = incident.pdschedule

        # deliberately update in this way the post_save signal gets sent
        # (required for the headline post to auto update)
        incident.report = report
        incident.summary = summary
        incident.impact = impact
        incident.lead = lead
        incident.severity = severity
        incident.pdschedule = pdschedule
        incident.save()


        if prev_schedule != pdschedule:
            res = settings.PDSESSION.rpost('/incidents',json={
                'incident':{
                    'type': 'incident',
                    'title': incident.report,
                    'service': {
                        'id': incident.pdschedule,
                        'type': 'service_reference',
                    },
                    'body': {
                        'type': 'incident_body',
                        'details': incident.summary if incident.summary else "",
                    },
                }
            })

    except Incident.DoesNotExist:
        logger.error(f"No incident found for pk {state}")

    except PDClientError as pce:
        logger.error(pce.response.json())
