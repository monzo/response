import json
import random

import pytest
from django.urls import reverse
from faker import Faker
from rest_framework.test import force_authenticate

from response import serializers
from response.core.views import IncidentActionViewSet
from response.models import Action
from tests.factories import ActionFactory, ExternalUserFactory, IncidentFactory

faker = Faker()


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
        assert "created_date" in action
        assert "due_date" in action
        assert "done_date" in action
        assert "priority" in action
        assert "type" in action


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
    assert Action.objects.filter(details=action_model.details).exists()


def test_update_action_user(arf, api_user):
    incident = IncidentFactory.create()
    user = ExternalUserFactory.create()

    action = incident.action_items()[0]

    action_data = serializers.ActionSerializer(action).data
    action_data["user"] = {
        "app_id": "slack",
        "display_name": user.display_name,
        "external_id": user.external_id,
        "full_name": user.full_name,
    }
    response = update_action(arf, api_user, incident.pk, action_data)
    print(response.rendered_content)
    assert response.status_code == 200, "Got non-201 response from API"

    updated_action = Action.objects.get(pk=action.pk)
    assert updated_action.user == user


def test_update_action(arf, api_user):
    incident = IncidentFactory.create()

    action = incident.action_items()[0]

    action_data = serializers.ActionSerializer(action).data

    action_data["details"] = faker.paragraph(nb_sentences=2, variable_nb_sentences=True)
    response = update_action(arf, api_user, incident.pk, action_data)
    print(response.rendered_content)
    assert response.status_code == 200, "Got non-201 response from API"

    updated_action = Action.objects.get(pk=action.pk)
    assert updated_action.details == action_data["details"]

    priorityChoices = ["1", "2", "3"]
    priorityChoices.remove(action.priority)
    action_data["done"] = not action_data["done"]
    action_data["priority"] = str(random.choice(priorityChoices))
    typeChoices = ["1", "2", "3"]
    typeChoices.remove(action.type)
    action_data["type"] = str(random.choice(typeChoices))
    action_data["done_date"] = faker.date_time_between(
        start_date=action.created_date, end_date="now"
    )
    action_data["due_date"] = faker.date_time_between(start_date="-6m", end_date="+6m")
    response = update_action(arf, api_user, incident.pk, action_data)
    print(response.rendered_content)
    assert response.status_code == 200, "Got non-201 response from API"

    updated_action = Action.objects.get(pk=action.pk)
    assert updated_action.done == action_data["done"]
    assert updated_action.priority == action_data["priority"]
    assert updated_action.type == action_data["type"]
    assert updated_action.done_date == action_data["done_date"]
    assert updated_action.due_date == action_data["due_date"]


def test_update_action_sanitized(arf, api_user):
    incident = IncidentFactory.create()
    action = incident.action_items()[0]
    action_data = serializers.ActionSerializer(action).data

    action_data["details"] = "<iframe>this should be escaped</iframe>"
    response = update_action(arf, api_user, incident.pk, action_data)
    assert response.status_code == 200, "Got non-201 response from API"

    updated_action = Action.objects.get(pk=action.pk)
    assert (
        updated_action.details == "&lt;iframe&gt;this should be escaped&lt;/iframe&gt;"
    )


def update_action(arf, api_user, incident_id, action_data):
    req = arf.put(
        reverse("incident-action-list", kwargs={"incident_pk": incident_id}),
        action_data,
        format="json",
    )
    force_authenticate(req, user=api_user)

    return IncidentActionViewSet.as_view({"put": "update"})(
        req, incident_pk=incident_id, pk=action_data["id"]
    )


def test_delete_action(arf, api_user):
    incident = IncidentFactory.create()
    user = ExternalUserFactory.create()

    action = ActionFactory.create(user=user, incident=incident)

    req = arf.delete(
        reverse("incident-action-list", kwargs={"incident_pk": incident.pk}),
        format="json",
    )
    force_authenticate(req, user=api_user)
    response = IncidentActionViewSet.as_view({"delete": "destroy"})(
        req, incident_pk=incident.pk, pk=action.pk
    )

    assert response.status_code == 204, "Got non-204 response from API"
    with pytest.raises(Action.DoesNotExist):
        Action.objects.get(pk=action.pk)
