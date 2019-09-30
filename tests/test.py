import json
import time
from datetime import datetime
from unittest import mock
from unittest.mock import ANY

import pytest
from django.urls import reverse

from response.core.models import ExternalUser, Incident


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
    mock_slack.dialog_open.assert_called_once_with(dialog=ANY, trigger_id="foo")


@pytest.mark.django_db(transaction=True)
def test_submit_dialog_creates_incident(post_from_slack_api, mock_slack):
    with mock.patch(
        "response.slack.dialog_handlers.get_user_profile",
        return_value={"name": "Opsy McOpsface"},
    ):

        mock_slack.send_or_update_message_block.return_value = {"ts": "123"}

        summary = "testing dialog submission"
        data = {
            "payload": json.dumps(
                {
                    "type": "dialog_submission",
                    "callback_id": "incident-report-dialog",
                    "user": {"id": "U123"},
                    "channel": {"id": "channel-posted-from"},
                    "response_url": "https://fake-response-url",
                    "submission": {
                        "report": "",
                        "summary": summary,
                        "impact": "",
                        "lead": "U123",
                        "severity": "",
                        "incident_type": "live",
                    },
                    "state": "foo",
                }
            )
        }
        r = post_from_slack_api("action", data)

        assert r.status_code == 200

        # Check if incident has been created

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

        # Check that headline post got created
        mock_slack.send_or_update_message_block.assert_called_with(
            "incident-channel-id", blocks=ANY, fallback_text=ANY, ts="123"
        )

        # Check that we sent an ephemeral message to the reporting user
        mock_slack.send_ephemeral_message.assert_called_with(
            "channel-posted-from", "U123", ANY
        )


@pytest.mark.django_db(transaction=True)
def test_submit_dialog_without_incident_type(post_from_slack_api, mock_slack):
    with mock.patch(
        "response.slack.dialog_handlers.get_user_profile",
        return_value={"name": "Opsy McOpsface"},
    ):

        mock_slack.send_or_update_message_block.return_value = {"ts": "123"}

        summary = "testing dialog submission"
        data = {
            "payload": json.dumps(
                {
                    "type": "dialog_submission",
                    "callback_id": "incident-report-dialog",
                    "user": {"id": "U123"},
                    "channel": {"id": "channel-posted-from"},
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

        # Check if incident has been created

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

        # Check that headline post got created
        mock_slack.send_or_update_message_block.assert_called_with(
            "incident-channel-id", blocks=ANY, fallback_text=ANY, ts="123"
        )

        # Check that we sent an ephemeral message to the reporting user
        mock_slack.send_ephemeral_message.assert_called_with(
            "channel-posted-from", "U123", ANY
        )


@pytest.mark.django_db(transaction=True)
def test_edit_incident(post_from_slack_api, mock_slack):

    mock_slack.send_or_update_message_block.return_value = {"ts": "123"}
    mock_slack.get_user_profile.return_value = {"ts": "123", "name": "Opsy McOpsface"}

    user = ExternalUser.objects.get_or_create(
        app_id="slack", external_id="U123", display_name="Opsy McOpsface"
    )[0]

    incident = Incident.objects.create_incident(
        report="Something happened",
        reporter=user,
        report_time=datetime.now(),
        report_only=False,
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
                    "severity": "1",
                    "incident_type": "",
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

    # Assert that the headline post gets updated
    mock_slack.send_or_update_message_block.assert_called_with(
        "incident-channel-id", blocks=ANY, fallback_text=ANY, ts="123"
    )
