from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from innotter.jwt_service import validate_token, decode_access_token
from user.models import User


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.get_full_path() in settings.AUTH_URL_PATH:
            return None

        access_token = request.headers.get('Authorization', None)
        if validate_token(access_token):
            payload = decode_access_token(access_token)
            user_uuid = payload.get('user_uuid')
            request.user = get_object_or_404(User, uuid=user_uuid)
            return None

        return JsonResponse(
            data={'message': 'Authorization not found. Please send valid token in headers'},
            status=401
        )
