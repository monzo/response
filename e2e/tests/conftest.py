from datetime import datetime
import os
import pytest
import requests


from requests import Session
from urllib.parse import urljoin

class ResponseSession(Session):
    def __init__(self, prefix_url="http://localhost:8000", username="admin", password="admin", *args, **kwargs):
        super(ResponseSession, self).__init__(*args, **kwargs)
        self.prefix_url = prefix_url
        self.auth = (username, password)

    def request(self, method, url, *args, **kwargs):
        url = urljoin(self.prefix_url, url)
        return super(ResponseSession, self).request(method, url, *args, **kwargs)


@pytest.fixture(scope="session")
def server_url():
    return os.getenv("RESPONSE_ADDR",  "http://localhost:8000")

@pytest.fixture(scope="session")
def client(server_url):
    s = ResponseSession(prefix_url=server_url)
    return s

@pytest.fixture(autouse=True,scope="session")
def wait_for_server(client):
    start_time = datetime.now()
    while True:
        try:
            r = client.get("core/")
            r.raise_for_status()
            return
        except:
            time_elapsed = datetime.now() - start_time
            if time_elapsed.total_seconds() >= 10:
                raise

