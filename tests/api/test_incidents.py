import json
import pytest
from rest_framework.test import force_authenticate
from django.urls import reverse

from response.serializers import IncidentSerializer
from response.core.views import IncidentViewSet
from tests.factories import IncidentFactory


@pytest.mark.django_db
def test_list_incidents(arf, api_user):
    persisted_incidents = IncidentFactory.create_batch(5)

    req = arf.get(reverse("Incidents-list"))
    force_authenticate(req, user=api_user)
    response = IncidentViewSet.as_view({"get": "list"})(req)

    assert response.status_code == 200
    content = json.loads(response.rendered_content)

    assert "results" in content
    incidents = content["results"]
    assert len(incidents) == len(persisted_incidents)

    for idx, incident in enumerate(incidents):
        assert incident["report_time"]

        # incidents should be in order of newest to oldest
        if idx != len(incidents) - 1:
            assert incident["report_time"] >= incidents[idx + 1]["report_time"]

        assert "end_time" in incident
        assert incident["impact"]
        assert incident["report"]
        assert incident["start_time"]
        assert incident["summary"]

        reporter = incident["reporter"]
        assert reporter["display_name"]
        assert reporter["external_id"]

        # TODO: verify actions are serialised inline

