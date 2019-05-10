import json
from datetime import datetime

from django.conf import settings

from slack.settings import INCIDENT_EDIT_DIALOG, INCIDENT_REPORT_DIALOG
from core.models.incident import Incident
from slack.models import HeadlinePost, CommsChannel
from slack.decorators import dialog_handler
from slack.slack_utils import send_ephemeral_message, channel_reference

import logging
logger = logging.getLogger(__name__)


@dialog_handler(INCIDENT_REPORT_DIALOG)
def report_incident(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    report = submission['report']
    summary = submission['summary']
    impact = submission['impact']
    lead = submission['lead']
    severity = submission['severity']

    Incident.objects.create_incident(
        report=report,
        reporter=user_id,
        report_time=datetime.now(),
        summary=summary,
        impact=impact,
        lead=lead,
        severity=severity,
    )

    incidents_channel_ref = channel_reference(settings.INCIDENT_CHANNEL_ID)
    text = f"Thanks for raising the incident 🙏\n\nHead over to {incidents_channel_ref} to complete the report and/or help deal with the issue"
    send_ephemeral_message(channel_id, user_id, text)


@dialog_handler(INCIDENT_EDIT_DIALOG)
def edit_incident(user_id: str, channel_id: str, submission: json, response_url: str, state: json):
    report = submission['report']
    summary = submission['summary']
    impact = submission['impact']
    lead = submission['lead']
    severity = submission['severity']

    try:
        incident = Incident.objects.get(pk=state)

        # deliberately update in this way the post_save signal gets sent
        # (required for the headline post to auto update)
        incident.report = report
        incident.summary = summary
        incident.impact = impact
        incident.lead = lead
        incident.severity = severity
        incident.save()

    except Incident.DoesNotExist:
        logger.error(f"No incident found for pk {state}")
