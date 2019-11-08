import factory
from django.db.models.signals import post_save
from faker import Factory

from response.core.models import Action

faker = Factory.create()


@factory.django.mute_signals(post_save)
class ActionFactory(factory.DjangoModelFactory):
    class Meta:
        model = Action

    user = factory.SubFactory("tests.factories.ExternalUserFactory")

    details = factory.LazyFunction(
        lambda: faker.paragraph(nb_sentences=1, variable_nb_sentences=True)
    )

    done = factory.LazyFunction(lambda: faker.boolean(chance_of_getting_true=25))
