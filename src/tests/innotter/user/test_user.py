import json

import pytest
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from user.models import User


class TestUserViewSet:
    @pytest.mark.django_db
    def test_success_user_registration(self, client, user_factory):
        url = reverse('user-list')
        user = user_factory.build()
        response = client.post(path=url,
                               data={"username": user.username,
                                     "password": user.password,
                                     "email": user.email},
                               format='json')
        assert response.status_code == 201
        assert User.objects.count() == 1
        assert response.data["email"] == user.email
        assert response.data["username"] == user.username

    @pytest.mark.django_db
    def test_fail_user_registration(self, client, user_factory):
        url = reverse('user-list')
        user = user_factory.build()
        response = client.post(path=url,
                               data={"username": user.username,
                                     "password": user.password},
                               format='json')
        assert 'email' in response.data
        assert response.status_code == 400
        assert User.objects.count() == 0

    @pytest.mark.django_db
    def test_success_user_login(self, client, user):
        url = reverse('user-login')
        response = client.post(path=url,
                               data={"email": user.email,
                                     "password": 'password'},
                               format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    @pytest.mark.django_db
    def test_fail_user_login(self, client, user):
        url = reverse('user-login')
        response = client.post(path=url,
                               data={"email": user.email,
                                     "password": 'wrong_password'},
                               format='json')
        assert response.status_code == 400
        assert 'access' not in response.data
        assert 'refresh' not in response.data

    @pytest.mark.django_db
    def test_refresh_token(self, client, auto_login):
        url = reverse('user-refresh')
        refresh = auto_login()
        response = client.post(path=url,
                               data={'refresh': f'Bearer {refresh}'},
                               format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    @pytest.mark.django_db
    def test_user_update(self, user_client):
        user, client = user_client
        url = reverse('user-detail', kwargs={"pk": user.id})
        response = client.patch(path=url,
                                data={"username": "another_username"})
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.username == "another_username"

    @pytest.mark.django_db
    def test_success_block_user(self, admin_client, user):
        admin, client = admin_client
        url = reverse('user-block-user', kwargs={"pk": user.id})
        response = client.post(path=url)
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.is_blocked is True

    @pytest.mark.django_db
    def test_fail_block_user(self, user_client):
        user, client = user_client
        url = reverse('user-block-user', kwargs={"pk": user.id})
        response = client.post(path=url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_unauthorized_access(self, client):
        url = reverse('user-list')
        response = client.get(path=url)
        assert response.status_code == 403
