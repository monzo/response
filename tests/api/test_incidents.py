import datetime
import json
import random

import pytest
from django.urls import reverse
from faker import Faker
from rest_framework.test import force_authenticate

from response import serializers
from response.core.views import IncidentsByMonthViewSet, IncidentViewSet
from response.models import ExternalUser, Incident
from tests.factories import IncidentFactory

faker = Faker()


def assert_incident_response(incident):
    assert incident["report_time"]

    assert "end_time" in incident  # end_time can be null for open incidents
    assert "is_closed" in incident  # this can be false
    assert incident["impact"]
    assert incident["report"]
    assert incident["start_time"]
    assert incident["summary"]
    assert incident["severity"]
    assert incident["comms_channel"]

    reporter = incident["reporter"]
    assert reporter["display_name"]
    assert reporter["external_id"]

    lead = incident["lead"]
    assert lead["display_name"]
    assert lead["external_id"]

    assert incident["action_items"]
    for action in incident["action_items"]:
        assert action["details"]
        assert "done" in action
        assert action["user"]


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

        assert_incident_response(incident)


def test_list_incidents_by_month(arf, api_user):
    IncidentFactory.create_batch(5)

    today = datetime.date.today()
    if today.month == 1:
        last_month = 12
        year = today.year - 1
    else:
        last_month = today.month - 1
        year = today.year

    req = arf.get(
        reverse(
            "incidents-bymonth-list",
            kwargs={"year": str(year), "month": f"{last_month:02d}"},
        )
    )
    print(req)
    force_authenticate(req, user=api_user)
    response = IncidentsByMonthViewSet.as_view({"get": "list"})(req, year, last_month)

    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    print(content)
    assert "results" in content, "Response didn't have results key"

    for incident in content["results"]:
        assert incident["report_time"]
        report_time = datetime.datetime.strptime(
            incident["report_time"], "%Y-%m-%dT%H:%M:%S"
        )
        assert report_time.month == last_month
        assert report_time.year == year

        assert_incident_response(incident)


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


@pytest.mark.parametrize(
    "update_key,update_value,expected_value",
    (
        (
            "impact",
            "<iframe>this should be escaped</iframe>",
            "&lt;iframe&gt;this should be escaped&lt;/iframe&gt;",
        ),
        (
            "report",
            "<script>alert('certainly shouldnt let this happen')</script>",
            "&lt;script&gt;alert('certainly shouldnt let this happen')&lt;/script&gt;",
        ),
        (
            "summary",
            '<meta http-equiv="refresh content=0;">',
            '&lt;meta http-equiv="refresh content=0;"&gt;',
        ),
    ),
)
def test_update_incident_sanitize_fields(
    arf, api_user, update_key, update_value, expected_value
):
    """
    Tests that we can't inject potentially dangerous HTML/JS into incident
    fields
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
        print(getattr(new_incident, update_key))
        assert (
            getattr(new_incident, update_key) == expected_value
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


def test_cannot_unset_severity(arf, api_user):
    """
    Tests that we cannot unset the incident severity
    """

    incident = IncidentFactory.create()
    serializer = serializers.IncidentSerializer(incident)
    updated = serializer.data

    updated["severity"] = None  # unset severity

    req = arf.put(
        reverse("incident-detail", kwargs={"pk": incident.pk}), updated, format="json"
    )
    force_authenticate(req, user=api_user)

    response = IncidentViewSet.as_view({"put": "update"})(req, pk=incident.pk)
    print(response.rendered_content)
    assert (
        response.status_code != 200
    ), "Got 200 response from API when we expected an error"


def test_cannot_access_incident_logged_out_if_configured(client, db, settings):
    settings.RESPONSE_LOGIN_REQUIRED = True

    incident = IncidentFactory()

    response = client.get(reverse("incident_doc", args=(incident.pk,)))

    assert response.status_code == 302
    assert response["location"].startswith(settings.LOGIN_URL)


def test_can_access_incident_logged_out_if_configured(client, db, settings):
    settings.RESPONSE_LOGIN_REQUIRED = False

    incident = IncidentFactory()

    response = client.get(reverse("incident_doc", args=(incident.pk,)))

    assert response.status_code == 200
