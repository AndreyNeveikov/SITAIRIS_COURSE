import factory
from user.models import User
from faker import Faker

fake = Faker()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Faker('first_name')
    email = factory.Faker('email')
    password = factory.PostGenerationMethodCall('set_password', 'password')
    role = 'user'
    is_staff = True
    is_superuser = True

