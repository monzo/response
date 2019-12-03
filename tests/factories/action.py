import random

import factory
from django.db.models.signals import post_save
from faker import Factory

from response.core.models import Action

faker = Factory.create()


@factory.django.mute_signals(post_save)
class ActionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Action

    created_date = factory.LazyFunction(
        lambda: faker.date_time_between(start_date="-6m", end_date="now", tzinfo=None)
    )

    user = factory.SubFactory("tests.factories.ExternalUserFactory")

    details = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=1, variable_nb_sentences=True)
    )

    done = factory.LazyFunction(lambda: faker.boolean(chance_of_getting_true=25))

    if done:
        done_date = factory.LazyAttribute(
            lambda a: faker.date_time_between(start_date=a.created_date, end_date="now")
        )

    if random.random() > 0.5:
        due_date = factory.LazyAttribute(
            lambda a: faker.date_time_between(start_date="-6m", end_date="+6m")
        )

    priority = factory.LazyFunction(lambda: str(random.randint(1, 3)))
    type = factory.LazyFunction(lambda: str(random.randint(1, 3)))
