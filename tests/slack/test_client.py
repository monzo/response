from unittest import mock

import pytest
import slackclient
from django.conf import settings

from response.slack import client
from tests.slack.slack_payloads import user_by_email


@pytest.fixture
def slack_api_mock(monkeypatch):
    client_mock = mock.Mock(spec=slackclient.SlackClient)
    monkeypatch.setattr(settings.SLACK_CLIENT, "client", client_mock)
    return client_mock


@pytest.fixture
def slack_client(slack_api_mock):
    # We set the backoff ridiculously low so that we're not hanging around
    # waiting for retries in tests
    c = client.SlackClient("test-token", retry_base_backoff_seconds=0.0000001)
    c.client = slack_api_mock
    return c


def test_slack_api_call_success(slack_client, slack_api_mock):
    expected_resp = {"ok": True, "response": "bar"}
    slack_api_mock.api_call.return_value = expected_resp

    resp = slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
    assert resp == expected_resp
    slack_api_mock.api_call.assert_called_with("test_endpoint", "arg1", kwarg2="foo")


def test_slack_api_call_error(slack_client, slack_api_mock):
    slack_api_mock.api_call.return_value = {"ok": False, "error": "test_error"}

    with pytest.raises(client.SlackError) as e:
        slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
        assert e.slack_error == "test_error"

    slack_api_mock.api_call.assert_called_with("test_endpoint", "arg1", kwarg2="foo")


def test_slack_backoff_rate_limit_succeeded(slack_client, slack_api_mock):
    expected_resp = {"ok": True, "response": "bar"}
    slack_api_mock.api_call.side_effect = [
        {"ok": False, "error": "ratelimited"},
        {"ok": False, "error": "ratelimited"},
        {"ok": False, "error": "ratelimited"},
        {"ok": False, "error": "ratelimited"},
        {"ok": False, "error": "ratelimited"},
        expected_resp,
    ]

    resp = slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
    assert resp == expected_resp
    assert slack_api_mock.api_call.call_count == 6


def test_slack_backoff_rate_limit_max_retry_attempts(slack_client, slack_api_mock):
    slack_api_mock.api_call.return_value = {"ok": False, "error": "ratelimited"}

    with pytest.raises(client.SlackError) as e:
        slack_client.api_call("test_endpoint", "arg1", kwarg2="foo")
        assert e.slack_error == "test_error"


def test_get_user_profile_by_email(slack_client, slack_api_mock):
    slack_api_mock.api_call.return_value = user_by_email

    # request a user by email
    user = slack_client.get_user_profile_by_email("spengler@ghostbusters.example.com")

    slack_api_mock.api_call.assert_called_with(
        "users.lookupByEmail", email="spengler@ghostbusters.example.com"
    )

    # check we get back the expected user profile
    assert user["id"] == "W012A3CDE"
    assert user["name"] == "spengler"
    assert user["fullname"] == "Egon Spengler"
    assert user["email"] == "spengler@ghostbusters.example.com"
