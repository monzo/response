import random

import factory
from faker import Factory

from response.core.models import Event

faker = Factory.create()


class EventFactory(factory.DjangoModelFactory):
    class Meta:
        model = Event

    timestamp = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-6m", end_date="now", tzinfo=None)
    )
    event_type = random.choice([Event.INCIDENT_EVENT_TYPE])

    # Using an Incident/Event factory here fails with a mysterious error:
    # https://github.com/pytest-dev/pytest-django/issues/713 (using @pytest.mark...
    # didn't resolve it). For now, a static fixture suffices.
    payload = {"report": "we are out of milk", "impact": "making tea is difficult"}
