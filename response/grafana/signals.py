import logging
from urllib.parse import urljoin

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.conf import settings

from response.grafana.client import GrafanaClient
from response.core.models import Incident

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Incident)
def update_grafana_annotation_after_incident_save(sender, instance: Incident, **kwargs):
    """
    Reflect changes to incidents in the grafana annotation

    Important: this is called in the synchronous /incident flow so must remain fast (<2 secs)

    """
    if settings.GRAFANA_CLIENT and instance.grafana_annotation_id:
        tags = ["incident", instance.severity_text()]
        text = "%s \n %s" % (instance.report, instance.summary)

        settings.GRAFANA_CLIENT.update_annotation(
            instance.grafana_annotation_id,
            time=instance.report_time,
            time_end=instance.end_time,
            text=text,
            tags=tags
        )

@receiver(pre_save, sender=Incident)
def create_grafana_annotation_before_incident_save(sender, instance: Incident, **kwargs):
    """
    Create a grafana annotation ticket before saving the incident

    Important: this is called in the synchronous /incident flow so must remain fast (<2 secs)

    """

    if settings.GRAFANA_CLIENT and not instance.grafana_annotation_id:
        tags = ["incident", instance.severity_text()]
        text = "%s \n %s" % (instance.report, instance.summary)
        start_time = int(instance.report_time.timestamp() * 1000)

        grafana_annotation = settings.GRAFANA_CLIENT.create_annotation(time=start_time, tags=tags, text=text)
        instance.grafana_annotation_id = grafana_annotation["id"]

