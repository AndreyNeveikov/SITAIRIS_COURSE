import factory

from page.models import Page, Tag
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


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: "tag #%s" % n)


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Page

    name = factory.Sequence(lambda n: "page #%s" % n)
    uuid = factory.Faker('ean')
    description = factory.Faker('text')
    image = factory.Faker('image_url')
    owner = factory.SubFactory(UserFactory)
    is_private = False

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            return
        if extracted:
            self.tags.set(*extracted)

    @factory.post_generation
    def add_tags(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for _ in range(extracted):
                self.tags.add(TagFactory())
