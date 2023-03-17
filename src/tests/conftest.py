import jwt
from django.conf import settings
from pytest import fixture
from pytest_factoryboy import register
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.innotter.factories import UserFactory, PageFactory, TagFactory, \
    PostFactory

register(UserFactory, 'user')
register(UserFactory, 'admin', role='admin', is_staff=True, is_superuser=True)
register(PageFactory, 'page')
register(TagFactory, 'tag')
register(PostFactory, 'post')


@fixture
def client():
    return APIClient()


@fixture
def get_auth_client():
    def wrapper(user):
        client = APIClient()
        access = get_access_token(user)
        client.credentials(Authorization=f'Bearer {access}')
        return client

    return wrapper


def get_access_token(user):
    access_payload = {
        'token_type': 'access',
        'exp': settings.ACCESS_TOKEN_LIFETIME,
        'user_uuid': str(user.uuid)
    }
    access_token = jwt.encode(payload=access_payload,
                              key=settings.ACCESS_TOKEN_KEY,
                              algorithm=settings.JWT_ALGORITHM)
    return access_token


@fixture
def refresh_token(db, client, user):
    url = reverse("user-login")
    response = client.post(
        path=url,
        data={"email": user.email,
              "password": "password"}
    )
    refresh_token = response.data["refresh"]

    return refresh_token
