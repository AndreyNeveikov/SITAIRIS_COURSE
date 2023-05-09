from rest_framework.routers import DefaultRouter

from core.views import BaseSearch, BaseSearch2
from user.views import UserViewSet
from page.views import PageViewSet, TagViewSet
from post.views import PostViewSet, FeedViewSet

router = DefaultRouter()
router.register(r'search', BaseSearch, basename='search')
router.register(r'user', UserViewSet, basename='user')
router.register(r'tag',  TagViewSet, basename='tag')
router.register(r'page', PageViewSet, basename='page')
router.register(r'post', PostViewSet, basename='post')
router.register(r'feed', FeedViewSet, basename='feed')
router.register(r'search2', BaseSearch2, basename='search2')

urlpatterns = router.urls
