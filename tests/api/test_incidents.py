from django.urls import reverse
from faker import Faker
from rest_framework.test import force_authenticate
import json
import pytest
import random

from response.models import Incident, ExternalUser
from response import serializers
from response.core.views import IncidentViewSet
from tests.factories import IncidentFactory

faker = Faker()


def test_list_incidents(arf, api_user):
    persisted_incidents = IncidentFactory.create_batch(5)

    req = arf.get(reverse("incident-list"))
    force_authenticate(req, user=api_user)
    response = IncidentViewSet.as_view({"get": "list"})(req)

    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    incidents = content["results"]
    assert len(incidents) == len(
        persisted_incidents
    ), "Didn't get expected number of incidents back"

    for idx, incident in enumerate(incidents):
        assert incident["report_time"]

        # incidents should be in order of newest to oldest
        if idx != len(incidents) - 1:
            assert (
                incident["report_time"] >= incidents[idx + 1]["report_time"]
            ), "Incidents are not in order of newest to oldest by report time"

        assert "end_time" in incident  # end_time can be null for open incidents
        assert incident["impact"]
        assert incident["report"]
        assert incident["start_time"]
        assert incident["summary"]
        assert incident["severity"]

        reporter = incident["reporter"]
        assert reporter["display_name"]
        assert reporter["external_id"]

        lead = incident["lead"]
        assert lead["display_name"]
        assert lead["external_id"]

        assert incident["comms_channel"]

        # TODO: verify actions are serialised inline


@pytest.mark.parametrize(
    "update_key,update_value",
    (
        ("", ""),  # no update
        ("impact", faker.paragraph(nb_sentences=2, variable_nb_sentences=True)),
        ("report", faker.paragraph(nb_sentences=1, variable_nb_sentences=True)),
        ("summary", faker.paragraph(nb_sentences=3, variable_nb_sentences=True)),
        (
            "start_time",
            faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None),
        ),
        (
            "end_time",
            faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None),
        ),
        ("severity", str(random.randint(1, 4))),
    ),
)
def test_update_incident(arf, api_user, update_key, update_value):
    """
    Tests that we can PUT /incidents/<pk> and mutate fields that get saved to
    the DB.
    """
    persisted_incidents = IncidentFactory.create_batch(5)

    incident = persisted_incidents[0]
    serializer = serializers.IncidentSerializer(incident)
    serialized = serializer.data

    updated = serialized
    del updated["reporter"]  # can't update reporter
    if update_key:
        updated[update_key] = update_value

    req = arf.put(
        reverse("incident-detail", kwargs={"pk": incident.pk}), updated, format="json"
    )
    force_authenticate(req, user=api_user)

    response = IncidentViewSet.as_view({"put": "update"})(req, pk=incident.pk)
    print(response.rendered_content)
    assert response.status_code == 200, "Got non-200 response from API"

    if update_key:
        new_incident = Incident.objects.get(pk=incident.pk)
        assert (
            getattr(new_incident, update_key) == update_value
        ), "Updated value wasn't persisted to the DB"


def test_update_incident_lead(arf, api_user):
    """
    Tests that we can update the incident lead by name
    """
    persisted_incidents = IncidentFactory.create_batch(5)

    incident = persisted_incidents[0]
    serializer = serializers.IncidentSerializer(incident)
    updated = serializer.data

    users = ExternalUser.objects.all()

    new_lead = users[0]
    while new_lead == incident.lead:
        new_lead = random.choices(users)

    updated["lead"] = serializers.ExternalUserSerializer(new_lead).data
    del updated["reporter"]  # can't update reporter

    req = arf.put(
        reverse("incident-detail", kwargs={"pk": incident.pk}), updated, format="json"
    )
    force_authenticate(req, user=api_user)

    response = IncidentViewSet.as_view({"put": "update"})(req, pk=incident.pk)
    print(response.rendered_content)
    assert response.status_code == 200, "Got non-200 response from API"

    new_incident = Incident.objects.get(pk=incident.pk)
    assert new_incident.lead == new_lead
