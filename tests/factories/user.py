import factory
from django.contrib.auth.models import User
from faker import Factory

from response.core.models import ExternalUser

faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda i: faker.user_name() + str(i))
    password = factory.LazyFunction(faker.password)


class ExternalUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExternalUser

    app_id = "slack"
    display_name = factory.LazyFunction(faker.name)
    external_id = factory.Sequence(lambda i: "U" + str(i).zfill(5))
    owner = factory.SubFactory("tests.factories.UserFactory")
