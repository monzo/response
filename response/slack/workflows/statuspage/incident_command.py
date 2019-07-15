from response.slack.workflows.statuspage.constants import *

from response.core.models import Incident
from response.slack.block_kit import Message, Button, Section, Actions, Text
from response.slack.models import CommsChannel


def handle_statuspage(incident: Incident, user_id: str, message: str):
    msg = Message()
    msg.add_block(Section(block_id="title", text=Text(f"To update the Statuspage, click below!")))
    msg.add_block(Actions(block_id="actions", elements=[
        Button("Update Statuspage", OPEN_STATUS_PAGE_DIALOG, value=incident.pk)
    ]))
    comms_channel = CommsChannel.objects.get(incident=incident)
    msg.send(comms_channel.channel_id)
    return True, None
