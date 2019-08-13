import pytest
from rest_framework.test import APIRequestFactory

from tests.factories import UserFactory, ExternalUserFactory

@pytest.fixture
def arf():
    return APIRequestFactory()


@pytest.fixture()
def api_user(transactional_db):
    e = ExternalUserFactory()
    return e.owner
