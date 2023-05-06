from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Innotter API",
        default_version='v1',
        description="Test description",
    ),
    public=True,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.v1.urls')),
    path(r'docs/', schema_view.with_ui('swagger', cache_timeout=0)),  # noqa
]
