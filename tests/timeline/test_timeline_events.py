import random

import pytest
from faker import Factory

from response.core.models import Incident, TimelineEvent
from tests.factories import ExternalUserFactory, IncidentFactory

faker = Factory.create()


@pytest.mark.django_db
def test_update_incident_lead():
    incident = IncidentFactory.create()
    new_lead = ExternalUserFactory.create()

    incident.lead = new_lead
    incident.save()

    event = TimelineEvent.objects.filter(
        incident=incident, event_type="incident_update"
    ).last()
    assert event.metadata["new_value"]["display_name"] == new_lead.display_name


@pytest.mark.django_db
def test_update_incident_report():
    incident = IncidentFactory.create()
    new_report = faker.paragraph(nb_sentences=3, variable_nb_sentences=True)

    incident.report = new_report
    incident.save()

    event = TimelineEvent.objects.filter(
        incident=incident, event_type="incident_update"
    ).last()
    assert event.metadata["new_value"] == new_report


@pytest.mark.django_db
def test_update_incident_summary():
    incident = IncidentFactory.create()
    new_summary = faker.paragraph(nb_sentences=3, variable_nb_sentences=True)

    incident.summary = new_summary
    incident.save()

    event = TimelineEvent.objects.filter(
        incident=incident, event_type="incident_update"
    ).last()
    assert event.metadata["new_value"] == new_summary


@pytest.mark.django_db
def test_update_incident_impact():
    incident = IncidentFactory.create()
    new_impact = faker.paragraph(nb_sentences=1)

    incident.impact = new_impact
    incident.save()

    event = TimelineEvent.objects.filter(
        incident=incident, event_type="incident_update"
    ).last()
    assert event.metadata["new_value"] == new_impact


@pytest.mark.django_db
def test_update_incident_severity():
    incident = IncidentFactory.create()
    new_severity = random.choice(
        [x for x, _ in Incident.SEVERITIES if x != incident.severity]
    )

    incident.severity = new_severity
    incident.save()

    event = TimelineEvent.objects.filter(
        incident=incident, event_type="incident_update"
    ).last()
    assert event.metadata["new_value"] == {
        "id": new_severity,
        "text": incident.severity_text(),
    }
