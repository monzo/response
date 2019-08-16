import json
import pytest
from django.urls import reverse
from rest_framework.test import force_authenticate

from response import serializers
from response.models import Action
from response.core.views import IncidentActionViewSet

from tests.factories import ActionFactory, ExternalUserFactory, IncidentFactory


def test_list_actions_by_incident(arf, api_user):
    incident = IncidentFactory.create()

    req = arf.get(reverse("incident-action-list", kwargs={"incident_pk": incident.pk}))
    force_authenticate(req, user=api_user)
    response = IncidentActionViewSet.as_view({"get": "list"})(
        req, incident_pk=incident.pk
    )

    content = json.loads(response.rendered_content)
    print(content)
    assert response.status_code == 200, "Got non-200 response from API"

    assert len(content["results"]) == len(incident.action_items())
    for action in content["results"]:
        assert action["details"]
        assert "done" in action
        assert action["user"]


def test_create_action(arf, api_user):
    incident = IncidentFactory.create()
    user = ExternalUserFactory.create()

    action_model = ActionFactory.build(user=user)
    action = serializers.ActionSerializer(action_model).data

    req = arf.post(
        reverse("incident-action-list", kwargs={"incident_pk": incident.pk}),
        action,
        format="json",
    )
    force_authenticate(req, user=api_user)
    response = IncidentActionViewSet.as_view({"post": "create"})(
        req, incident_pk=incident.pk
    )

    assert response.status_code == 201, "Got non-201 response from API"

    new_action = Action.objects.get(details=action_model.details)

