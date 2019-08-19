import factory
from faker import Factory

from response.core.models import TimelineEvent

from .user import ExternalUserFactory

faker = Factory.create()

class TimelineEventFactory(factory.DjangoModelFactory):
    class Meta:
        model = TimelineEvent

    incident = factory.SubFactory('tests.factories.IncidentFactory')

    timestamp = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)
    )
    text = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=5, variable_nb_sentences=True)
    )
    event_type = "text"
