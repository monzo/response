from django.db.models.signals import post_save
from django.core.signals import request_finished
from django.dispatch import receiver

from response.core.models import Incident
from response.slack.models import HeadlinePost

from time import sleep


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


@receiver(post_save, sender=HeadlinePost)
def update_headline_after_save(sender, instance, **kwargs):
    """
    Reflect changes to headline posts in slack

    """
    instance.update_in_slack()
