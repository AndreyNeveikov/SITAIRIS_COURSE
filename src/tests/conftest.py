import jwt
from django.conf import settings
from pytest import fixture
from pytest_factoryboy import register
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from tests.innotter.factories import UserFactory

register(UserFactory, 'user')
register(UserFactory, 'admin', role='admin', is_staff=True, is_superuser=True)


@fixture
def client():
    return APIClient()


@fixture
def user_client(user_and_access_token):
    client = APIClient()
    user, access = user_and_access_token()
    client.credentials(Authorization=f'Bearer {access}')
    return user, client


@fixture
def admin_client(user_and_access_token):
    client = APIClient()
    user, access = user_and_access_token(is_admin=True)
    client.credentials(Authorization=f'Bearer {access}')
    return user, client


@fixture
def user_and_access_token(user, admin):
    def wrapper(is_admin=False):
        access_payload = {
            'token_type': 'access',
            'exp': settings.ACCESS_TOKEN_LIFETIME,
            'user_uuid': str(admin.uuid if is_admin else user.uuid)
        }

        access_token = jwt.encode(payload=access_payload,
                                  key=settings.ACCESS_TOKEN_KEY,
                                  algorithm=settings.JWT_ALGORITHM)
        return user, access_token

    return wrapper


@fixture
def user_and_refresh_token(user, admin):
    def wrapper(is_admin=False):
        refresh_payload = {
            'token_type': 'refresh',
            'exp': settings.REFRESH_TOKEN_LIFETIME,
            'user_uuid': str(admin.uuid if is_admin else user.uuid)
        }

        refresh_token = jwt.encode(payload=refresh_payload,
                                   key=settings.REFRESH_TOKEN_KEY,
                                   algorithm=settings.JWT_ALGORITHM)
        return user, refresh_token

    return wrapper


@fixture
def auto_login(db, client, user, admin):
    def wrapper(is_admin=False):
        url = reverse("user-login")
        response = client.post(
            path=url,
            data={"email": admin.email if is_admin else user.email,
                  "password": "password"}
        )
        refresh_token = response.data["refresh"]

        return refresh_token

    return wrapper
