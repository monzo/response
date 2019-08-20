from urllib.parse import urljoin

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from django.urls import reverse

from response.core.models import Incident
from response.slack.models import HeadlinePost


@receiver(post_save, sender=Incident)
def update_headline_after_incident_save(sender, instance, **kwargs):
    """
    Reflect changes to incidents in the headline post

    Important: this is called in the synchronous /incident flow so must remain fast (<2 secs)

    """
    try:
        headline_post = HeadlinePost.objects.get(
            incident=instance
        )
        headline_post.update_in_slack()

    except HeadlinePost.DoesNotExist:
        headline_post = HeadlinePost.objects.create_headline_post(
            incident=instance
        )


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
            reverse('incident_doc', kwargs={'incident_id': instance.pk})
        )
        settings.SLACK_CLIENT.send_message(
            user_to_notify.external_id, f"👋 Don't forget to fill out an incident report here: {doc_url}")


@receiver(post_save, sender=HeadlinePost)
def update_headline_after_save(sender, instance, **kwargs):
    """
    Reflect changes to headline posts in slack

    """
    instance.update_in_slack()
