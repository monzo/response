import pytest
from rest_framework.test import APIRequestFactory

from tests.factories import UserFactory

@pytest.fixture
def arf():
    return APIRequestFactory()


@pytest.fixture
def api_user():
    return UserFactory()
