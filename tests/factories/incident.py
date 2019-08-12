import random

import factory
from faker import Factory

from response.core.models import Incident

from .user import ExternalUserFactory

faker = Factory.create()


class IncidentFactory(factory.DjangoModelFactory):
    class Meta:
        model = Incident

    if random.random() > .5:
        lead = factory.SubFactory(ExternalUserFactory)

    impact = faker.paragraph(nb_sentences=1, variable_nb_sentences=True)
    report = faker.paragraph(nb_sentences=3, variable_nb_sentences=True)
    report_time = faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)
    reporter = factory.SubFactory(ExternalUserFactory)
    start_time = faker.date_time_between(start_date="-3d", end_date="now", tzinfo=None)

    if random.random() > .5:
        end_time = faker.date_between(start_date="-3d", end_date="today")
        end_time = factory.LazyAttribute(lambda a: faker.date_between(start_date=a.start_time, end_date="today"))


    severity = str(random.randint(1, 4))
    summary = faker.paragraph(nb_sentences=3, variable_nb_sentences=True)
