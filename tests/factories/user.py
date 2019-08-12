from django.contrib.auth.models import User
import factory
from faker import Factory


from response.core.models import ExternalUser

faker = Factory.create()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyFunction(faker.user_name)
    password = factory.LazyFunction(faker.password)


class ExternalUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExternalUser

    app_id = "slack"
    display_name = factory.LazyFunction(faker.name)
    external_id = factory.LazyFunction(lambda: "U" + faker.word())
    owner = factory.SubFactory("tests.factories.UserFactory")
