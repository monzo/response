from response.core.models.incident import Incident

from response.slack.models import CommsChannel
from response.slack.decorators import keyword_handler

import logging
logger = logging.getLogger(__name__)


@keyword_handler(['status page', 'statuspage'])
def status_page_notification(comms_channel: CommsChannel, user: str, text: str, ts: str):
    comms_channel.post_in_channel("ℹ️ You mentiond the Status Page - <http://google.com|here's the runbook> on how to put it up.")
