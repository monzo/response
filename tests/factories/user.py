from django.contrib.auth.models import User
import factory
from faker import Factory


from response.core.models import ExternalUser

faker = Factory.create()

class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

class ExternalUserFactory(factory.DjangoModelFactory):
    class Meta:
        model = ExternalUser

    app_id = "slack"
    display_name = faker.name()
    external_id = "U" + faker.word()

