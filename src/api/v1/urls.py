from rest_framework.routers import DefaultRouter

from core.views import BaseSearch
from user.views import UserViewSet
from page.views import PageViewSet
from post.views import PostViewSet, FeedViewSet

router = DefaultRouter()
router.register(r'', BaseSearch, basename='search')
router.register(r'user', UserViewSet, basename='user')
router.register(r'page', PageViewSet, basename='page')
router.register(r'post', PostViewSet, basename='post')
router.register(r'feed', FeedViewSet, basename='feed')

urlpatterns = router.urls
