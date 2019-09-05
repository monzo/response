import hashlib
import hmac
import os
from datetime import datetime
from urllib.parse import urljoin

import pytest
from requests import Request, Session


class ResponseSession(Session):
    """ResponseSession
    A requests.Session that automatically prefixes the base
    URL of the response server and adds authentication.
    """

    def __init__(
        self,
        prefix_url="http://localhost:8000",
        username="admin",
        password="admin",
        *args,
        **kwargs,
    ):
        super(ResponseSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.auth = (username, password)

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(ResponseSession, self).request(method, url, *args, **kwargs)


@pytest.fixture(scope="session")
def server_url():
    return os.getenv("RESPONSE_ADDR", "http://localhost:8000")


@pytest.fixture(scope="session")
def client(server_url):
    s = ResponseSession(prefix_url=server_url)
    return s


@pytest.fixture(autouse=True, scope="session")
def wait_for_server(client):
    start_time = datetime.now()
    while True:
        try:
            r = client.get("core/")
            r.raise_for_status()
            return
        except Exception:
            time_elapsed = datetime.now() - start_time
            if time_elapsed.total_seconds() >= 60:
                print(f"time elapsed: {time_elapsed.total_seconds()}s")
                raise


class ResponseSlackSession(Session):
    """ResponseSlackSession
    A requests.Session that can make authenticated & signed requests to the
    response Slack webhook API.
    """

    def __init__(self, secret="", prefix_url="http://localhost:8000", *args, **kwargs):
        """__init__

        :param secret: Slack signing secret - this can be anything, but must match what is given to the response server
        :param prefix_url: Base URL of the response server
        """
        super(ResponseSlackSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.secret = secret

    def generate_signature(self, secret, data):
        timestamp = str(int(datetime.now().timestamp()))
        req = str.encode("v0:" + str(timestamp) + ":") + data

        signature = (
            "v0=" + hmac.new(str.encode(secret), req, hashlib.sha256).hexdigest()
        )

        return timestamp, signature

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)

        req = Request(method, url, *args, **kwargs)
        prepped = self.prepare_request(req)

        timestamp, signature = self.generate_signature(
            self.secret, prepped.body.encode()
        )

        prepped.headers["X-Slack-Request-Timestamp"] = timestamp
        prepped.headers["X-Slack-Signature"] = signature

        settings = self.merge_environment_settings(prepped.url, {}, None, None, None)
        return super(ResponseSlackSession, self).send(prepped, **settings)


@pytest.fixture(scope="session")
def slack_signing_secret():
    return os.getenv("SLACK_SIGNING_SECRET", "shh-this-has-been-set-in-tests")


@pytest.fixture(scope="session")
def slack_client(slack_signing_secret, server_url):
    c = ResponseSlackSession(secret=slack_signing_secret, prefix_url=server_url)
    return c


@pytest.fixture
def slack_httpserver(httpserver):
    """slack_httpserver
    A fixture that can listen for requests from response to the Slack API, and
    respond with JSON stubs.
    """
    httpserver.expect_request(method="POST", uri="/api/dialog.open").respond_with_json(
        {"ok": True}
    )

    httpserver.expect_request(method="POST", uri="/api/users.info").respond_with_json(
        {
            "ok": True,
            "user": {
                "name": "Opsy McOpsface",
                "profile": {"real_name": "Opsy McOpsface"},
            },
        }
    )

    httpserver.expect_request(
        method="POST", uri="/api/chat.postMessage"
    ).respond_with_json({"ok": True, "ts": "123"})

    httpserver.expect_request(method="POST", uri="/api/chat.update").respond_with_json(
        {"ok": True}
    )

    yield httpserver
    httpserver.clear_all_handlers()
    httpserver.clear_assertions()
