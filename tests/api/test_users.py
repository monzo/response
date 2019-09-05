import json

from django.urls import reverse
from rest_framework.test import force_authenticate

from response.core.views import ExternalUserViewSet
from tests.factories import ExternalUserFactory


def test_list_users(arf, api_user):
    users = ExternalUserFactory.create_batch(5)

    req = arf.get(reverse("externaluser-list"))
    force_authenticate(req, user=api_user)
    response = ExternalUserViewSet.as_view({"get": "list"})(req)

    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"

    assert len(content["results"]) == (
        len(users) + 1
    )  # account for the API user we created in a fixture

    for user in content["results"]:
        assert user["app_id"]
        assert user["external_id"]
        assert user["display_name"]
