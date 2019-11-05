from datetime import datetime

from response.core.models import Incident

from django.db.models.signals import pre_save
from django.dispatch import receiver

import logging
logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Incident)
def prompt_incident_report(sender, instance: Incident, **kwargs):
    logger.info(f"emitting event for incident {instance}")