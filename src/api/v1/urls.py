from rest_framework.routers import DefaultRouter

from user.views import UserViewSet
from page.views import PageViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'page', PageViewSet)

urlpatterns = router.urls
