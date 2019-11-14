import json
from datetime import datetime, timedelta

from django.urls import reverse
from rest_framework.test import force_authenticate

from response.core.signals import ActionEventHandler, IncidentEventHandler
from response.core.views import EventsViewSet
from tests.factories.action import ActionFactory
from tests.factories.event import EventFactory
from tests.factories.incident import IncidentFactory


def test_generate_incident_event(arf, api_user):
    incident = IncidentFactory()
    IncidentEventHandler.handle(None, incident)

    req = arf.get(reverse("event-list"))
    force_authenticate(req, user=api_user)

    response = EventsViewSet.as_view({"get": "list"})(req)
    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == 1, "Expected one event"


def test_generate_action_event(arf, api_user):
    incident = IncidentFactory()
    action = ActionFactory.create(incident=incident)
    ActionEventHandler.handle(None, action)

    req = arf.get(reverse("event-list"))
    force_authenticate(req, user=api_user)

    response = EventsViewSet.as_view({"get": "list"})(req)
    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == 1, "Expected one event"


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
        assert event["payload"]["report"]


def test_filter_events(arf, api_user):
    ts = datetime.now() + timedelta(days=30)
    EventFactory(timestamp=ts)

    query_params = {"from": ts - timedelta(hours=1), "to": ts + timedelta(hours=1)}
    req = arf.get(reverse("event-list"), data=query_params)
    force_authenticate(req, user=api_user)

    response = EventsViewSet.as_view({"get": "list"})(req)
    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == 1, "Expected one event"


def test_omit_private_incident(arf, api_user):
    incident = IncidentFactory(private=True)
    IncidentEventHandler.handle(None, incident)

    req = arf.get(reverse("event-list"))
    force_authenticate(req, user=api_user)

    response = EventsViewSet.as_view({"get": "list"})(req)
    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == 0, "Expected zero events"


def test_omit_private_action(arf, api_user):
    incident = IncidentFactory(private=True)
    action = ActionFactory.create(incident=incident)
    ActionEventHandler.handle(None, action)

    req = arf.get(reverse("event-list"))
    force_authenticate(req, user=api_user)

    response = EventsViewSet.as_view({"get": "list"})(req)
    assert response.status_code == 200, "Got non-200 response from API"
    content = json.loads(response.rendered_content)

    assert "results" in content, "Response didn't have results key"
    events = content["results"]
    assert len(events) == 0, "Expected zero events"
