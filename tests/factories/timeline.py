import random

import factory
from faker import Factory

from response.core.models import TimelineEvent

faker = Factory.create()


class TimelineEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = TimelineEvent

    incident = factory.SubFactory("tests.factories.IncidentFactory")

    timestamp = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)
    )
    text = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=3, variable_nb_sentences=True)
    )
    event_type = factory.LazyFunction(
        lambda: random.choice(["text", "slack_pin", "incident_update"])
    )

    @factory.lazy_attribute
    def metadata(self):
        if self.event_type == "text":
            return None
        elif self.event_type == "slack_pin":
            return {
                "author": {"display_name": "foo"},
                "message_ts": "12345679.0",
                "channel_id": "C12345",
            }
        elif self.event_type == "incident_update":
            return {
                "update_type": "summary",
                "old_value": faker.paragraph(
                    nb_sentences=3, variable_nb_sentences=True
                ),
                "new_value": faker.paragraph(
                    nb_sentences=3, variable_nb_sentences=True
                ),
            }
