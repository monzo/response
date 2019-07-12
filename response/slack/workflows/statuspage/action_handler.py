import requests
import response.slack.dialog_builder as dialog_bld

from response.slack.workflows.statuspage.connections import get_status_page_conn

from response.slack.decorators import ActionContext
from response.core.models import IncidentExtension
from response.slack.block_kit import Text

OPEN_STATUS_PAGE_DIALOG = 'open-status-page-dialog'
STATUS_PAGE_UPDATE = 'status-page-update'


def handle_open_status_page_dialog(ac: ActionContext):
    statuspage_incident_id, created = IncidentExtension.objects.get_or_create(incident=ac.incident, key='statuspage_incident_id')

    if statuspage_incident_id.value:
        # Get the first incident in the list where id matches
        incident = next((i for i in  get_status_page_conn().incidents.list() if i['id'] == statuspage_incident_id.value))
        values = {
            'name': incident['name'],
            'status': incident['status'],
            'message': incident['incident_updates'][0]['body'], # We only need the latest update [0]
            'impact_override': incident['impact_override']
        }
    else:
        values = {}

    # Can't make any further updates once resolved
    if values.get("status") == 'resolved':
        requests.post(ac.response_url,
                      json=Text(f'The status page can\'t be updated after it has been resolved.').serialize())
        return

    dialog = dialog_bld.Dialog(
        title="Statuspage Update",
        submit_label="Update",
        state=ac.incident.pk,
        elements=[
            dialog_bld.Text(label="Name", name="name", value=values.get("name"), hint="Make this concise and clear - it's what will show in the apps"),
            dialog_bld.SelectWithOptions([
                ("Investigating", "investigating"),
                ("Identified", "identified"),
                ("Monitoring", "monitoring"),
                ("Resolved", "resolved"),
            ], label="Status", name="incident_status", value=values.get("status")),
            dialog_bld.TextArea(label="Description", name="message", optional=True, value=values.get("message")),
            dialog_bld.SelectWithOptions([
                ("No - don't share on Twitter", "False"),
                ("Yes - post to Twitter", "True"),
            ], label="Send to Twitter?", name="wants_twitter_update", optional=True),
            dialog_bld.SelectWithOptions([
                ("Major", "major"),
                ("Critical", "critical"),
            ], label="Severity", name="impact_override", optional=True, value=values.get("impact_override"))
        ]
    )

    dialog.send_open_dialog(STATUS_PAGE_UPDATE, ac.trigger_id)
