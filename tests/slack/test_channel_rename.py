import pytest

from response.slack.event_handlers import handle_channel_rename
from tests.factories import IncidentFactory


@pytest.mark.django_db
def test_handle_channel_rename(mock_slack):
    incident = IncidentFactory.create()

    handle_channel_rename(incident, {"channel": {"name": "new-channel-name"}})
    assert incident.comms_channel().channel_name == "new-channel-name"
