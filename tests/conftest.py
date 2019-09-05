import os
from datetime import datetime
from unittest.mock import MagicMock
from urllib.parse import urlencode

import pytest
from django.conf import settings
from django.urls import reverse

from response.slack.authentication import generate_signature
from response.slack.client import SlackClient


@pytest.fixture(autouse=True)
def mock_slack(monkeypatch):
    mock_slack = MagicMock(spec=SlackClient(""))
    mock_slack.get_channel_name.return_value = "#inc-test-channel"
    mock_slack.send_or_update_message_block.return_value = {"ok": True, "ts": 1234}
    monkeypatch.setattr(settings, "SLACK_CLIENT", mock_slack)
    return mock_slack


@pytest.fixture(scope="session")
def slack_signing_secret():
    return os.getenv("SLACK_SIGNING_SECRET", "signingsecretnotset")


@pytest.fixture
def post_from_slack_api(client, slack_signing_secret):
    def _post(url_name, data):
        form = urlencode(data).encode()
        timestamp = str(int(datetime.now().timestamp()))
        signature = generate_signature(timestamp, slack_signing_secret, form)

        return client.post(
            reverse(url_name),
            data=form,
            content_type="application/x-www-form-urlencoded",
            HTTP_X_SLACK_REQUEST_TIMESTAMP=timestamp,
            HTTP_X_SLACK_SIGNATURE=signature,
        )

    return _post
