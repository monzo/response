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
    return "http://localhost:8000"

@pytest.fixture(scope="session")
def client(server_url):
    s = ResponseSession(prefix_url=server_url)
    return s

@pytest.fixture(autouse=True,scope="session")
def check_health(client):
    r = client.get("core/")
    r.raise_for_status()

