from datetime import datetime, timedelta

import pytest
from rest_framework.reverse import reverse


@pytest.mark.django_db
class TestPageViewSet:
    def test_success_page_create(self, user, get_auth_client,
                                 page_factory, tag):
        url = reverse('page-list')
        client = get_auth_client(user)
        page = page_factory.build()
        response = client.post(path=url,
                               data={"uuid": page.uuid,
                                     "name": page.name,
                                     "description": page.description,
                                     "tags": [tag.name]},
                               format='json')
        assert response.status_code == 201
        assert response.data['uuid'] == page.uuid
        assert response.data['name'] == page.name
        assert response.data['description'] == page.description
        assert response.data['tags'] == [tag.id]
        assert response.data['owner'] == user.id

    def test_fail_page_create(self, user, get_auth_client, page_factory):
        url = reverse('page-list')
        client = get_auth_client(user)
        page = page_factory.build()
        response = client.post(path=url,
                               data={"uuid": page.uuid,
                                     "name": page.name},
                               format='json')
        assert response.status_code == 400

    def test_page_update(self, user, get_auth_client, page):
        url = reverse('page-detail', kwargs={'pk': page.id})
        page_name_before_update = page.name
        client = get_auth_client(user)
        response = client.patch(path=url,
                                data={"name": "another_name"},
                                format='json')
        page.refresh_from_db()
        assert response.status_code == 200
        assert page_name_before_update != page.name

    def test_page_retrieve(self, user, get_auth_client, page):
        url = reverse('page-detail', kwargs={'pk': page.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 200

    def test_success_page_list_for_admin(self, admin, get_auth_client):
        url = reverse('page-list')
        client = get_auth_client(admin)
        response = client.get(path=url)
        assert response.status_code == 200

    def test_fail_page_list_for_user(self, user, get_auth_client):
        url = reverse('page-list')
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 403

    def test_success_page_block_for_admin(self, admin, get_auth_client,
                                          page, mock_block_task):
        url = reverse('page-block-page', kwargs={"pk": page.id})
        client = get_auth_client(admin)
        page_status_before_block = page.is_blocked
        unblock_date = (datetime.today() + timedelta(days=1)).isoformat('T')
        response = client.post(path=url,
                               data={"is_blocked": True,
                                     "unblock_date": unblock_date},
                               format='json')
        page.refresh_from_db()
        assert response.status_code == 202
        assert page.is_blocked is True
        assert page.is_blocked != page_status_before_block

    def test_fail_page_block_for_user(self, user, get_auth_client, page):
        url = reverse('page-block-page', kwargs={"pk": page.id})
        client = get_auth_client(user)
        unblock_date = (datetime.today() + timedelta(days=1)).isoformat('T')
        response = client.post(path=url,
                               data={"is_blocked": True,
                                     "unblock_date": unblock_date},
                               format='json')
        assert response.status_code == 403

    def test_retrieve_blocked_page(self, user, get_auth_client, page_factory):
        page = page_factory(is_blocked=True)
        url = reverse('page-detail', kwargs={"pk": page.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 403

    def test_follow_public_page(self, page_factory, get_auth_client):
        page_1, page_2 = page_factory(), page_factory()
        user_1 = page_1.owner
        client_1 = get_auth_client(user_1)

        url = reverse('page-follow', kwargs={"pk": page_2.id})
        response = client_1.get(path=url)

        page_2.refresh_from_db()
        assert response.status_code == 202
        assert user_1 in page_2.followers.all()

    def test_follow_private_page(self, page_factory, get_auth_client):
        page_1, page_2 = page_factory(), page_factory(is_private=True)
        user_1 = page_1.owner
        client_1 = get_auth_client(user_1)

        url = reverse('page-follow', kwargs={"pk": page_2.id})
        response = client_1.get(path=url)

        page_2.refresh_from_db()
        assert response.status_code == 202
        assert user_1 not in page_2.followers.all()
        assert user_1 in page_2.follow_requests.all()

    def test_accept_follow_request(self, page_factory, get_auth_client):
        page_1, page_2 = page_factory(), page_factory(is_private=True)
        user_1, user_2 = page_1.owner, page_2.owner
        client_1, client_2 = get_auth_client(user_1), get_auth_client(user_2)

        url_follow = reverse('page-follow', kwargs={"pk": page_2.id})
        response_1 = client_1.get(path=url_follow)

        url_accept_follow = reverse('page-accept-follow-request',
                                    kwargs={"pk": page_2.id})
        response_2 = client_2.post(path=url_accept_follow,
                                   data={"follow_requests": user_1.id},
                                   format='json')
        page_1.refresh_from_db()
        page_2.refresh_from_db()
        assert response_1.status_code == 202
        assert response_2.status_code == 200
        assert user_1 in page_2.followers.all()

    def test_decline_follow_request(self, page_factory, get_auth_client):
        page_1, page_2 = page_factory(), page_factory(is_private=True)
        user_1, user_2 = page_1.owner, page_2.owner
        client_1, client_2 = get_auth_client(user_1), get_auth_client(user_2)

        url_follow = reverse('page-follow', kwargs={"pk": page_2.id})
        response_1 = client_1.get(path=url_follow)

        url_accept_follow = reverse('page-decline-follow-request',
                                    kwargs={"pk": page_2.id})
        response_2 = client_2.post(path=url_accept_follow,
                                   data={"follow_requests": user_1.id},
                                   format='json')
        page_2.refresh_from_db()
        assert response_1.status_code == 202
        assert response_2.status_code == 200
        assert user_1 not in page_2.followers.all()
        assert user_1 not in page_2.follow_requests.all()

    def test_retrieve_private_page_by_not_follower(self, user, page_factory,
                                                   get_auth_client):
        page = page_factory.create(is_private=True)
        url = reverse('page-detail', kwargs={"pk": page.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 200
        assert 'uuid' not in response.data
