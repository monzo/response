from django.conf import settings

INCIDENT_REPORT_DIALOG = "incident-report-dialog"
INCIDENT_EDIT_DIALOG = "incident-edit-dialog"

PAGERDUTY_ENABLED = getattr(settings, 'PAGERDUTY_ENABLED', False)
