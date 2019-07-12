import pytest

import hashlib
import hmac
import json
from requests import Request, Session
from urllib.parse import urljoin,urlencode
from datetime import datetime


class ResponseSlackSession(Session):
    def __init__(self, secret="", prefix_url="http://localhost:8000", username="admin", password="admin", *args, **kwargs):
        super(ResponseSlackSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.auth = (username, password)
        self.secret = secret

    def generate_signature(self, secret, data):
        timestamp = str(int(datetime.now().timestamp()))
        req = str.encode('v0:' + str(timestamp) + ':') + data

        signature = 'v0=' + hmac.new(
            str.encode(secret),
            req, hashlib.sha256
        ).hexdigest()

        return timestamp, signature


    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)

        req = Request(method, url, *args, **kwargs)
        prepped = self.prepare_request(req)

        timestamp, signature = self.generate_signature(self.secret, prepped.body.encode())


        prepped.headers["X-Slack-Request-Timestamp"] = timestamp
        prepped.headers["X-Slack-Signature"] = signature


        settings = self.merge_environment_settings(prepped.url, {}, None, None, None)
        return super(ResponseSlackSession, self).send(
            prepped, **settings
        )

@pytest.fixture(scope="session")
def slack_signing_secret():
    return "0fb064cb851b5bd336614ea00e9ec1a8"

@pytest.fixture(scope="session")
def slack_client(slack_signing_secret, server_url):
    c = ResponseSlackSession(secret=slack_signing_secret, prefix_url=server_url)
    return c
