from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from innotter.jwt_service import MiddlewareTokenService


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):  # noqa
        token_service = MiddlewareTokenService(request)
        if token_service.token:
            token_service.is_valid()
            user = token_service.get_user_from_payload()
            request.user = user

        return None
