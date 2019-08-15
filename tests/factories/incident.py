import random

from django.db.models.signals import post_save
import factory
from faker import Factory

from response.core.models import Incident, ExternalUser
from response.slack.models import CommsChannel

faker = Factory.create()

class CommsChannelFactory(factory.DjangoModelFactory):
    class Meta:
        model = CommsChannel


@factory.django.mute_signals(post_save)
class IncidentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Incident

    impact = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=1, variable_nb_sentences=True)
    )
    report = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=3, variable_nb_sentences=True)
    )
    report_time = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)
    )

    reporter = factory.SubFactory("tests.factories.ExternalUserFactory")
    lead = factory.SubFactory("tests.factories.ExternalUserFactory")

    start_time = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)
    )

    if random.random() > 0.5:
        end_time = factory.LazyAttribute(
            lambda a: faker.date_time_between(start_date=a.start_time, end_date="now")
        )

    severity = factory.LazyFunction(lambda: str(random.randint(1, 4)))
    summary = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=3, variable_nb_sentences=True)
    )

    related_channel = factory.RelatedFactory(CommsChannelFactory, 'incident')
