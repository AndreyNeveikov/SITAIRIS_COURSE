from rest_framework.routers import DefaultRouter

from user.views import UserViewSet

router = DefaultRouter()
router.register(r'user', UserViewSet)

urlpatterns = router.urls
