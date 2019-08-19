import json

from django.urls import reverse
from faker import Faker
import pytest
from rest_framework.test import force_authenticate

from response import serializers
from response.models import TimelineEvent
from response.core.views import IncidentTimelineEventViewSet

from tests.factories import IncidentFactory, TimelineEventFactory

faker = Faker()


def test_create_timeline_event(arf, api_user):
    incident = IncidentFactory.create()

    event_model = TimelineEventFactory.build(incident=incident)
    event_data = serializers.TimelineEventSerializer(event_model).data

    req = arf.post(
        reverse("incident-timeline-event-list", kwargs={"incident_pk": incident.pk}),
        event_data,
        format="json",
    )
    force_authenticate(req, user=api_user)
    response = IncidentTimelineEventViewSet.as_view({"post": "create"})(
        req, incident_pk=incident.pk
    )

    assert response.status_code == 201, "Got non-201 response from API"

    new_action = TimelineEvent.objects.get(
        incident=incident, timestamp=event_model.timestamp
    )


def test_list_actions_by_incident(arf, api_user):
    incident = IncidentFactory.create()

    req = arf.get(
        reverse("incident-timeline-event-list", kwargs={"incident_pk": incident.pk})
    )
    force_authenticate(req, user=api_user)
    response = IncidentTimelineEventViewSet.as_view({"get": "list"})(
        req, incident_pk=incident.pk
    )

    content = json.loads(response.rendered_content)
    print(content)
    assert response.status_code == 200, "Got non-200 response from API"

    assert len(content["results"]) == len(incident.timeline_events())
    for event in content["results"]:
        assert event["timestamp"]
        assert event["text"]
        assert event["event_type"]


@pytest.mark.parametrize(
    "update_key,update_value",
    (
        ("", ""),  # no update
        (
            "timestamp",
            faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None),
        ),
        ("text", faker.paragraph(nb_sentences=5, variable_nb_sentences=True)),
    ),
)
def test_update_timeline_event(arf, api_user, update_key, update_value):
    incident = IncidentFactory.create()

    event_model = incident.timeline_events()[0]
    event_data = serializers.TimelineEventSerializer(event_model).data

    if update_key:
        event_data[update_key] = update_value

    req = arf.put(
        reverse("incident-timeline-event-list", kwargs={"incident_pk": incident.pk}),
        event_data,
        format="json",
    )
    force_authenticate(req, user=api_user)
    response = IncidentTimelineEventViewSet.as_view({"put": "update"})(
        req, incident_pk=incident.pk, pk=event_model.pk
    )

    assert response.status_code == 200, "Got non-200 response from API"
    if update_key:
        new_event = TimelineEvent.objects.get(pk=event_model.pk)
        assert (
            getattr(new_event, update_key) == update_value
        ), "Updated value wasn't persisted to the DB"


def test_delete_timeline_event(arf, api_user):
    incident = IncidentFactory.create()

    event_model = incident.timeline_events()[0]

    req = arf.delete(
        reverse("incident-timeline-event-list", kwargs={"incident_pk": incident.pk})
    )
    force_authenticate(req, user=api_user)
    response = IncidentTimelineEventViewSet.as_view({"delete": "destroy"})(
        req, incident_pk=incident.pk, pk=event_model.pk
    )

    assert response.status_code == 204, "Got non-204 response from API"
    with pytest.raises(TimelineEvent.DoesNotExist):
        TimelineEvent.objects.get(pk=event_model.pk)
