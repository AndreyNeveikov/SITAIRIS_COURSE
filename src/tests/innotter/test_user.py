import pytest
from rest_framework.reverse import reverse

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
    def test_refresh_token(self, client, refresh_token):
        url = reverse('user-refresh')
        response = client.post(path=url,
                               data={'refresh': f'Bearer {refresh_token}'},
                               format='json')
        assert response.status_code == 200
        assert 'access' in response.data
        assert 'refresh' in response.data

    @pytest.mark.django_db
    def test_user_update(self, user, get_auth_client):
        client = get_auth_client(user)
        username_before_update = user.username
        url = reverse('user-detail', kwargs={"pk": user.id})
        response = client.patch(path=url,
                                data={"username": "another_username"})
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.username != username_before_update
        assert user.username == "another_username"

    @pytest.mark.django_db
    def test_success_block_user(self, admin, get_auth_client, user):
        client = get_auth_client(admin)
        url = reverse('user-block-user', kwargs={"pk": user.id})
        response = client.post(path=url)
        user.refresh_from_db()
        assert response.status_code == 200
        assert user.is_blocked is True

    @pytest.mark.django_db
    def test_fail_block_user(self, user, get_auth_client):
        client = get_auth_client(user)
        url = reverse('user-block-user', kwargs={"pk": user.id})
        response = client.post(path=url)
        assert response.status_code == 403

    @pytest.mark.django_db
    def test_unauthorized_access(self, client):
        url = reverse('user-list')
        response = client.get(path=url)
        assert response.status_code == 403
