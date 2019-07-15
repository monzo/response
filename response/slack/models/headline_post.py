from django.conf import settings
from django.db import models
from django.urls import reverse
from urllib.parse import urljoin

from response.core.models.incident import Incident
from response.slack.models.comms_channel import CommsChannel

from response.slack.block_kit import *
from response.slack.slack_utils import user_reference, channel_reference


class HeadlinePostManager(models.Manager):
    def create_headline_post(self, incident):
        headline_post = self.create(
            incident=incident,
        )
        headline_post.update_in_slack()
        return headline_post


class HeadlinePost(models.Model):

    EDIT_INCIDENT_BUTTON = "edit-incident-button"
    CLOSE_INCIDENT_BUTTON = "close-incident-button"
    CREATE_COMMS_CHANNEL_BUTTON = "create-comms-channel-button"
    PAGE_ON_CALL_BUTTON = "page-on-call-button"

    objects = HeadlinePostManager()
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    message_ts = models.CharField(max_length=20, null=True)
    comms_channel = models.OneToOneField(CommsChannel, on_delete=models.DO_NOTHING, null=True)

    def update_in_slack(self):
        "Creates/updates the slack headline post with the latest incident info"
        msg = Message()

        # Set the fallback text so notifications look nice
        msg.set_fallback_text(f"{self.incident.report} reported by {user_reference(self.incident.reporter)}")

        # Add report/people
        msg.add_block(Section(block_id="report", text=Text(f"*{self.incident.report}*")))
        msg.add_block(Section(block_id="reporter", text=Text(f"🙋🏻‍♂️ Reporter: {user_reference(self.incident.reporter.external_id)}")))
        incident_lead_text = user_reference(self.incident.lead.external_id) if self.incident.lead else "-"
        msg.add_block(Section(block_id="lead", text=Text(f"👩‍🚒 Incident Lead: {incident_lead_text}")))

        msg.add_block(Divider())

        # Add additional info
        msg.add_block(Section(block_id="status", text=Text(f"{self.incident.status_emoji()} Status: {self.incident.status_text().capitalize()}")))
        severity_text = self.incident.severity_text().capitalize() if self.incident.severity_text() else "-"
        msg.add_block(Section(block_id="severity", text=Text(f"{self.incident.severity_emoji()} Severity: {severity_text}")))

        doc_url = urljoin(
            settings.SITE_URL,
            reverse('incident_doc', kwargs={'incident_id': self.incident.pk})
        )
        msg.add_block(Section(block_id="incident_doc", text=Text(f"📄 Document: <{doc_url}|Incident {self.incident.pk}>")))

        channel_ref = channel_reference(self.comms_channel.channel_id) if self.comms_channel else None
        if channel_ref:
            msg.add_block(Section(block_id="comms_channel", text=Text(f"🗣 Comms Channel: {channel_ref or '-'}")))

        # Add buttons (if the incident is open)
        if not self.incident.is_closed():
            msg.add_block(Section(text=Text("Need something else?")))
            actions = Actions(block_id="actions")

            if not self.comms_channel:
                actions.add_element(Button(":speaking_head_in_silhouette: Create Comms Channel", self.CREATE_COMMS_CHANNEL_BUTTON, value=self.incident.pk))

            if settings.PAGERDUTY_ENABLED:
                confirm = Confirm("Page an On-caller", "Are you sure you want to page someone?", "Yes - I need help now!", "No")
                actions.add_element(Button(":pager: Page On-call", self.PAGE_ON_CALL_BUTTON, value=self.incident.pk, confirm=confirm))

            actions.add_element(Button(":pencil2: Edit", self.EDIT_INCIDENT_BUTTON, value=self.incident.pk))

            actions.add_element(Button(":white_check_mark: Close", self.CLOSE_INCIDENT_BUTTON, value=self.incident.pk))

            msg.add_block(actions)

        # Post / update the slack message
        response = msg.send(settings.INCIDENT_CHANNEL_ID, self.message_ts)

        # Save the message ts identifier if not already set
        if not self.message_ts:
            self.message_ts = response['ts']
            self.save()
