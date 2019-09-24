from unittest import mock

from django.conf import settings
import pytest
import slackclient

from response.slack import client


@pytest.fixture
def mock_slack_client(monkeypatch):
    client_mock = mock.Mock(spec=slackclient.SlackClient)
    monkeypatch.setattr(settings.SLACK_CLIENT, "client", client_mock)
    return client_mock


def test_slack_api_call(mock_slack_client):

    response_slack_client = client.SlackClient("test-token")
    response_slack_client.client = mock_slack_client

    expected_resp = {"ok": True, "response": "bar"}
    mock_slack_client.api_call.return_value = expected_resp

    resp = response_slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
    assert resp == expected_resp
    mock_slack_client.api_call.assert_called_with("test_endpoint", "arg1", kwarg2="foo")

    mock_slack_client.api_call.return_value = {"ok": False, "error": "test_error"}

    with pytest.raises(client.SlackError) as e:
        response_slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
        assert e.error == "test_error"
