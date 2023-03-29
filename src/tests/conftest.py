from unittest.mock import Mock

import jwt
from django.conf import settings
from pytest import fixture
from pytest_factoryboy import register
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
def refresh_token(user):
    refresh_payload = {
        'token_type': 'refresh',
        'exp': settings.REFRESH_TOKEN_LIFETIME,
        'user_uuid': str(user.uuid)
    }
    refresh_token = jwt.encode(payload=refresh_payload,
                               key=settings.REFRESH_TOKEN_KEY,
                               algorithm=settings.JWT_ALGORITHM)
    return refresh_token


@fixture(autouse=True)
def mock_producer_publish(mocker):
    mocker.patch('core.producer.publish', Mock())


@fixture
def mock_redis_login(mocker, refresh_token):
    mocker.patch('user.serializers.redis.set', Mock())


@fixture
def mock_redis_refresh_token(mocker, refresh_token):
    mocker.patch('user.serializers.redis.get',
                 return_value=bytes(f'Bearer {refresh_token}', 'utf-8'))
    mocker.patch('user.serializers.redis.set', Mock())


@fixture
def mock_block_task(mocker):
    mocker.patch('page.serializers.PageService.unblock_page_task', Mock())


@fixture
def mock_send_email(mocker):
    mocker.patch('post.views.send_email', Mock())
