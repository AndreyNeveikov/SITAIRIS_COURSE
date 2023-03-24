import pytest
from rest_framework.reverse import reverse

from post.models import Post


@pytest.mark.django_db
class TestPostViewSet:
    def test_success_post_create(self, get_auth_client, page,
                                 post_factory, mock_send_email):
        url = reverse('post-list')
        post = post_factory.build()
        client = get_auth_client(page.owner)
        response = client.post(path=url,
                               data={"page": page.id,
                                     "content": post.content},
                               format='json')
        assert response.status_code == 201
        assert response.data['page'] == page.id
        assert response.data['content'] == post.content
        assert Post.objects.count() == 1

    def test_fail_post_create(self, get_auth_client, page,
                              page_factory, post_factory):
        url = reverse('post-list')
        post = post_factory.build()
        another_user_page = page_factory.create()
        client = get_auth_client(page.owner)
        response = client.post(path=url,
                               data={"page": another_user_page.id,
                                     "content": post.content},
                               format='json')
        assert response.status_code == 400
        assert Post.objects.count() == 0

    def test_success_post_update(self, get_auth_client, post, post_factory):
        url = reverse('post-detail', kwargs={"pk": post.id})
        post_old_content = post.content
        post_new_content = post_factory().content
        client = get_auth_client(post.page.owner)
        response = client.patch(path=url,
                                data={"content": post_new_content},
                                format='json')
        post.refresh_from_db()
        assert response.status_code == 200
        assert post.content != post_old_content

    def test_fail_not_own_post_update(self, get_auth_client, post_factory):
        post_user_1, post_user_2 = post_factory.create(), post_factory.create()
        url = reverse('post-detail', kwargs={"pk": post_user_2.id})
        client = get_auth_client(post_user_1.page.owner)
        response = client.patch(path=url,
                                data={"content": post_factory().content},
                                format='json')
        assert response.status_code == 403

    def test_success_own_post_destroy(self, get_auth_client, post):
        url = reverse('post-detail', kwargs={"pk": post.id})
        client = get_auth_client(post.page.owner)
        response = client.delete(path=url)
        assert response.status_code == 204
        assert Post.objects.count() == 0

    def test_fail_not_own_post_destroy(self, get_auth_client,
                                       post_factory, user):
        not_own_post = post_factory.create()
        url = reverse('post-detail', kwargs={"pk": not_own_post.id})
        client = get_auth_client(user)
        response = client.delete(path=url)
        assert response.status_code == 403
        assert Post.objects.count() == 1

    def test_success_post_list(self, admin, get_auth_client):
        url = reverse('post-list')
        client = get_auth_client(admin)
        response = client.get(path=url)
        assert response.status_code == 200

    def test_fail_post_list(self, user, get_auth_client):
        url = reverse('post-list')
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 403

    def test_authorized_post_retrieve(self, user, get_auth_client, post):
        url = reverse('post-detail', kwargs={"pk": post.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 200

    def test_unauthorized_post_retrieve(self, client, post):
        url = reverse('post-detail', kwargs={"pk": post.id})
        response = client.get(path=url)
        assert response.status_code == 403

    def test_post_like(self, user, get_auth_client, post):
        post_likes_before_like = post.liked_by.count()
        url = reverse('post-like', kwargs={"pk": post.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        post.refresh_from_db()
        assert response.status_code == 200
        assert post.liked_by.count() != post_likes_before_like
        assert user in post.liked_by.all()

    def test_post_unlike(self, user, get_auth_client, post):
        post.liked_by.add(user)
        post_likes_after_like = post.liked_by.count()
        url = reverse('post-like', kwargs={"pk": post.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        post.refresh_from_db()
        assert response.status_code == 200
        assert post.liked_by.count() != post_likes_after_like
        assert user not in post.liked_by.all()

    def test_show_user_liked_posts(self, user, get_auth_client, post):
        post.liked_by.add(user)
        url = reverse('post-liked-posts')
        client = get_auth_client(user)
        response = client.get(path=url)
        post.refresh_from_db()
        assert response.status_code == 200
        assert Post.objects.filter(liked_by=user).count() == 1

    def test_show_post_like_users_list(self, user, get_auth_client, post):
        post.liked_by.add(user)
        url = reverse('post-like-users-list', kwargs={"pk": post.id})
        client = get_auth_client(user)
        response = client.get(path=url)
        assert response.status_code == 200
        assert user in post.liked_by.all()
