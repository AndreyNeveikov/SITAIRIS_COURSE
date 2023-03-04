from rest_framework.routers import DefaultRouter

from user.views import UserViewSet
from page.views import PageViewSet
from post.views import PostViewSet, FeedViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'page', PageViewSet)
router.register(r'post', PostViewSet)
router.register(r'feed', FeedViewSet)

urlpatterns = router.urls
