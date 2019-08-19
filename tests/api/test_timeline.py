from django.urls import reverse
from rest_framework.test import force_authenticate

from response import serializers
from response.models import TimelineEvent
from response.core.views import IncidentTimelineEventViewSet

from tests.factories import IncidentFactory, TimelineEventFactory


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
