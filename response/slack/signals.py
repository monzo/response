from urllib.parse import urljoin

from django.conf import settings
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse

from response.core.models import Incident, add_incident_update_event
from response.core.serializers import ExternalUserSerializer
from response.slack.models import HeadlinePost


@receiver(post_save, sender=Incident)
def update_headline_after_incident_save(sender, instance, **kwargs):
    """
    Reflect changes to incidents in the headline post

    Important: this is called in the synchronous /incident flow so must remain fast (<2 secs)

    """
    try:
        headline_post = HeadlinePost.objects.get(incident=instance)
        headline_post.update_in_slack()

    except HeadlinePost.DoesNotExist:
        headline_post = HeadlinePost.objects.create_headline_post(incident=instance)


@receiver(pre_save, sender=Incident)
def prompt_incident_report(sender, instance: Incident, **kwargs):
    """
    Prompt incident lead to complete a report when an incident is closed.
    """

    try:
        prev_state = Incident.objects.get(pk=instance.pk)
    except Incident.DoesNotExist:
        # Incident hasn't been saved yet, nothing to do here.
        return

    if instance.is_closed() and not prev_state.is_closed():
        user_to_notify = instance.lead or instance.reporter
        doc_url = urljoin(
            settings.SITE_URL,
            reverse("incident_doc", kwargs={"incident_id": instance.pk}),
        )
        settings.SLACK_CLIENT.send_message(
            user_to_notify.external_id,
            f"👋 Don't forget to fill out an incident report here: {doc_url}",
        )


@receiver(post_save, sender=HeadlinePost)
def update_headline_after_save(sender, instance, **kwargs):
    """
    Reflect changes to headline posts in slack

    """
    instance.update_in_slack()


@receiver(pre_save, sender=Incident)
def add_timeline_events(sender, instance: Incident, **kwargs):
    try:
        prev_state = Incident.objects.get(pk=instance.pk)
    except Incident.DoesNotExist:
        # Incident hasn't been saved yet, nothing to do here.
        return

    if prev_state.lead != instance.lead:
        update_incident_lead_event(prev_state, instance)

    if prev_state.report != instance.report:
        update_incident_report_event(prev_state, instance)

    if prev_state.summary != instance.summary:
        update_incident_summary_event(prev_state, instance)

    if prev_state.impact != instance.impact:
        update_incident_impact_event(prev_state, instance)

    if prev_state.severity != instance.severity:
        update_incident_severity_event(prev_state, instance)


def update_incident_lead_event(prev_state, instance):
    old_lead = None
    if prev_state.lead:
        old_lead = ExternalUserSerializer(prev_state.lead).data

    new_lead = None
    if instance.lead:
        new_lead = ExternalUserSerializer(instance.lead).data

    if prev_state.lead:
        if instance.lead:
            text = f"Incident lead changed from {prev_state.lead.display_name} to {instance.lead.display_name}"
        else:
            text = f"{prev_state.lead.display_name} was removed as incident lead"

    else:
        text = f"{instance.lead.display_name} was added as incident lead"

    add_incident_update_event(
        incident=instance,
        update_type="incident_lead",
        text=text,
        old_value=old_lead,
        new_value=new_lead,
    )


def update_incident_report_event(prev_state, instance):
    add_incident_update_event(
        incident=instance,
        update_type="incident_report",
        text=f'Incident report updated from "{prev_state.report}" to "{instance.report}"',
        old_value=prev_state.report,
        new_value=instance.report,
    )


def update_incident_summary_event(prev_state, instance):
    if prev_state.summary:
        text = f'Incident summary updated from "{prev_state.summary}" to "{instance.summary}"'
    else:
        text = f'Incident summary added: "{instance.summary}"'

    add_incident_update_event(
        incident=instance,
        update_type="incident_summary",
        text=text,
        old_value=prev_state.summary,
        new_value=instance.summary,
    )


def update_incident_impact_event(prev_state, instance):
    if prev_state.impact:
        text = (
            f'Incident impact updated from "{prev_state.impact}" to "{instance.impact}"'
        )
    else:
        text = f'Incident impact added: "{instance.impact}"'

    add_incident_update_event(
        incident=instance,
        update_type="incident_impact",
        text=text,
        old_value=prev_state.impact,
        new_value=instance.impact,
    )


def update_incident_severity_event(prev_state, instance):
    if prev_state.severity:
        text = f"Incident severity updated from {prev_state.severity_text()} to {instance.severity_text()}"
    else:
        text = f"Incident severity set to {instance.severity_text()}"

    add_incident_update_event(
        incident=instance,
        update_type="incident_severity",
        text=text,
        old_value={
            "id": prev_state.severity,
            "text": prev_state.severity_text() if prev_state else "",
        },
        new_value={"id": instance.severity, "text": instance.severity_text()},
    )
