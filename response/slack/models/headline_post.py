import logging
from urllib.parse import urljoin

from django.conf import settings
from django.db import models
from django.urls import reverse

from response.core.models.incident import Incident
from response.slack.block_kit import Actions, Button, Divider, Message, Section, Text
from response.slack.client import SlackError
from response.slack.decorators.headline_post_action import (
    SLACK_HEADLINE_POST_ACTION_MAPPINGS,
    headline_post_action,
)
from response.slack.models.comms_channel import CommsChannel
from response.slack.reference_utils import channel_reference, user_reference

logger = logging.getLogger(__name__)


class HeadlinePostManager(models.Manager):
    def create_headline_post(self, incident):
        headline_post = self.create(incident=incident)
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
    comms_channel = models.OneToOneField(
        CommsChannel, on_delete=models.DO_NOTHING, null=True
    )

    def update_in_slack(self):
        "Creates/updates the slack headline post with the latest incident info"
        logging.info(f"Updating headline post in Slack for incident {self.incident.pk}")
        msg = Message()

        # Set the fallback text so notifications look nice
        msg.set_fallback_text(
            f"{self.incident.report} reported by {user_reference(self.incident.reporter)}"
        )

        # Add report/people
        msg.add_block(
            Section(block_id="report", text=Text(f"*{self.incident.report}*"))
        )
        msg.add_block(
            Section(
                block_id="reporter",
                text=Text(
                    f"🙋🏻‍♂️ Reporter: {user_reference(self.incident.reporter.external_id)}"
                ),
            )
        )
        incident_lead_text = (
            user_reference(self.incident.lead.external_id)
            if self.incident.lead
            else "-"
        )
        msg.add_block(
            Section(
                block_id="lead", text=Text(f"👩‍🚒 Incident Lead: {incident_lead_text}")
            )
        )

        msg.add_block(Divider())

        # Add additional info
        msg.add_block(
            Section(
                block_id="status",
                text=Text(
                    f"{self.incident.status_emoji()} Status: {self.incident.status_text().capitalize()}"
                ),
            )
        )
        severity_text = (
            self.incident.severity_text().capitalize()
            if self.incident.severity_text()
            else "-"
        )
        msg.add_block(
            Section(
                block_id="severity",
                text=Text(
                    f"{self.incident.severity_emoji()} Severity: {severity_text}"
                ),
            )
        )

        doc_url = urljoin(
            settings.SITE_URL,
            reverse("incident_doc", kwargs={"incident_id": self.incident.pk}),
        )
        msg.add_block(
            Section(
                block_id="incident_doc",
                text=Text(f"📄 Document: <{doc_url}|Incident {self.incident.pk}>"),
            )
        )

        if not self.incident.report_only:
            channel_ref = (
                channel_reference(self.comms_channel.channel_id)
                if self.comms_channel
                else None
            )
            if channel_ref:
                msg.add_block(
                    Section(
                        block_id="comms_channel",
                        text=Text(f"🗣 Comms Channel: {channel_ref or '-'}"),
                    )
                )

        # Add buttons (if the incident is open)
        if not self.incident.is_closed():
            msg.add_block(Section(text=Text("Need something else?")))
            actions = Actions(block_id="actions")

            # Add all actions mapped by @headline_post_action decorators
            for key in sorted(SLACK_HEADLINE_POST_ACTION_MAPPINGS.keys()):
                funclist = SLACK_HEADLINE_POST_ACTION_MAPPINGS[key]
                for f in funclist:
                    action = f(self)
                    if action:
                        actions.add_element(action)

            msg.add_block(actions)

        # Post / update the slack message
        if self.incident.report_only and hasattr(
            settings, "INCIDENT_REPORT_CHANNEL_ID"
        ):
            channel_id = settings.INCIDENT_REPORT_CHANNEL_ID
        else:
            channel_id = settings.INCIDENT_CHANNEL_ID

        try:
            response = msg.send(channel_id, self.message_ts)
            logger.info(
                f"Got response back from Slack after updating headline post: {response}"
            )

            # Save the message ts identifier if not already set
            if not self.message_ts:
                self.message_ts = response["ts"]
                self.save()
        except SlackError as e:
            logger.error(
                f"Failed to update headline post in {channel_id} with ts {self.message_ts}. Error: {e}"
            )

    def post_to_thread(self, message):
        settings.SLACK_CLIENT.send_message(
            settings.INCIDENT_CHANNEL_ID, message, thread_ts=self.message_ts
        )


# Default/core actions to display on headline post.
# In order to allow inserting actions between these ones we increment the order by 100


@headline_post_action(order=100)
def create_comms_channel_action(headline_post):
    if headline_post.incident.report_only:
        # Reports don't link to comms channels
        return None
    if headline_post.comms_channel:
        # No need to create an action, channel already exists
        return None
    return Button(
        ":speaking_head_in_silhouette: Create Comms Channel",
        HeadlinePost.CREATE_COMMS_CHANNEL_BUTTON,
        value=headline_post.incident.pk,
    )


@headline_post_action(order=200)
def edit_incident_button(headline_post):
    return Button(
        ":pencil2: Edit",
        HeadlinePost.EDIT_INCIDENT_BUTTON,
        value=headline_post.incident.pk,
    )


@headline_post_action(order=300)
def close_incident_button(headline_post):
    return Button(
        ":white_check_mark: Close",
        HeadlinePost.CLOSE_INCIDENT_BUTTON,
        value=headline_post.incident.pk,
    )
