import json

from django.urls import reverse
from rest_framework.test import force_authenticate

from response.core.views import EventsViewSet
from tests.factories.event import EventFactory


def test_list_events(arf, api_user):
    persisted_events = EventFactory.create_batch(10)

    req = arf.get(reverse("event-list"))
    force_authenticate(req, user=api_user)
    response = EventsViewSet.as_view({"get": "list"})(req)

    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == len(
        persisted_events
    ), "Didn't get expected number of events back"

    for event in events:
        assert event["timestamp"]
        assert event["event_type"]
        payload = json.loads(event["payload"])
        assert payload["report"]
