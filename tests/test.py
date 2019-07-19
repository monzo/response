from datetime import datetime
import json
import time
from unittest.mock import MagicMock

import pytest
from django.urls import reverse

from response.core.models import Incident, ExternalUser



def test_slash_command_invalid_signature(client):
    timestamp = str(int(datetime.now().timestamp()))
    signature = "v0=0d055ef102d1d89ab8f233d6c345bc0fad85116fdf616cc541e3fb7584617d83"

    r = client.post(
        reverse("slash_command"),
        data=b"",
        content_type="application/x-www-form-urlencoded",
        HTTP_X_SLACK_REQUEST_TIMESTAMP=timestamp,
        HTTP_X_SLACK_SIGNATURE=signature,
    )

    assert r.status_code == 403



def test_slash_command_invokes_dialog(post_from_slack_api, mock_slack):
    data = {"user_id": "U123", "trigger_id": "foo"}
    r = post_from_slack_api("slash_command", data)

    assert r.status_code == 200

    call = mock_slack.slack_api_calls["dialog.open"]
    assert call
    assert call["kwargs"]["trigger_id"] == "foo"


@pytest.mark.django_db(transaction=True)
def test_submit_dialog_creates_incident(post_from_slack_api, mock_slack):

    summary = "testing dialog submission"
    data = {
        "payload": json.dumps(
            {
                "type": "dialog_submission",
                "callback_id": "incident-report-dialog",
                "user": {"id": "U123"},
                "channel": {"id": "D123"},
                "response_url": "https://fake-response-url",
                "submission": {
                    "report": "",
                    "summary": summary,
                    "impact": "",
                    "lead": "U123",
                    "severity": "",
                },
                "state": "foo",
            }
        )
    }
    r = post_from_slack_api("action", data)

    assert r.status_code == 200

    start_time = datetime.now()
    timeout_secs = 2
    backoff = 0.1
    q = Incident.objects.filter(summary=summary)

    while True:
        d = datetime.now() - start_time
        if d.total_seconds() > timeout_secs:
            pytest.fail(f"waited {timeout_secs}s for condition")
            return
        time.sleep(backoff)

        if q.exists():
            break

    assert "chat.postMessage" in mock_slack.slack_api_calls
    assert "chat.update" in mock_slack.slack_api_calls
    assert "chat.postEphemeral" in mock_slack.slack_api_calls


@pytest.mark.django_db(transaction=True)
def test_edit_incident(post_from_slack_api, mock_slack):

    user = ExternalUser.objects.get_or_create(
        app_id="slack", external_id="U123", display_name="Opsy McOpsface"
    )[0]

    incident = Incident.objects.create_incident(
        report="Something happened",
        reporter=user,
        report_time=datetime.now(),
        summary="Testing editing incidents - before",
        impact="Lots",
        lead=user,
        severity="1",
    )

    newsummary = "Testing editing incidents - after"
    data = {
        "payload": json.dumps(
            {
                "type": "dialog_submission",
                "callback_id": "incident-edit-dialog",
                "user": {"id": "U123"},
                "channel": {"id": "D123"},
                "response_url": "https://fake-response-url",
                "submission": {
                    "report": "",
                    "summary": newsummary,
                    "impact": "",
                    "lead": "U123",
                    "severity": "",
                },
                "state": incident.id,
            }
        )
    }
    r = post_from_slack_api("action", data)

    assert r.status_code == 200

    start_time = datetime.now()
    timeout_secs = 2
    backoff = 0.2
    i = Incident.objects.filter(summary=newsummary)
    while True:
        d = datetime.now() - start_time
        if d.total_seconds() > timeout_secs:
            pytest.fail(f"waited {timeout_secs}s for condition")
            return
        time.sleep(backoff)

        if i.exists():
            break

    assert "chat.postMessage" in mock_slack.slack_api_calls
    assert "chat.update" in mock_slack.slack_api_calls
    assert "users.info" in mock_slack.slack_api_calls
