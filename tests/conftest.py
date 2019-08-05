from datetime import datetime
import os
from urllib.parse import urlencode

from django.urls import reverse
from django.conf import settings

import pytest
from unittest.mock import MagicMock

from response.slack import dialog_builder, slack_utils, block_kit
from response.slack.authentication import generate_signature
from response.slack.client import SlackClient

@pytest.fixture()
def mock_slack(monkeypatch):
    mock_slack = MagicMock(spec=SlackClient(""))
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

