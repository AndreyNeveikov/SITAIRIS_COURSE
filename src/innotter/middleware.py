import jwt

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from user.models import User


class JWTAuthMiddleware(MiddlewareMixin):
    @staticmethod
    def check_if_access_token_exist(access_token):
        return access_token and access_token.startswith(settings.AUTH_HEADER_PREFIX)

    def process_request(self, request):
        if request.get_full_path() in settings.AUTH_URL_PATH:
            return None

        access_token = request.headers.get('Authorization', None)

        if not self.check_if_access_token_exist(access_token):
            return JsonResponse(
                data={'message': 'Authorization not found. Please send valid token in headers'},
                status=401
            )
        try:
            payload = jwt.decode(
                jwt=access_token.replace(settings.AUTH_HEADER_PREFIX, ''),
                key=settings.ACCESS_TOKEN_KEY,
                algorithms=settings.JWT_ALGORITHM
            )
            user_uuid = payload.get('user_uuid')
            request.user = get_object_or_404(User, uuid=user_uuid)
            return None
        except jwt.ExpiredSignatureError:
            return JsonResponse(
                data={'message': 'Authentication token has expired'},
                status=401
            )
        except (jwt.InvalidTokenError, jwt.DecodeError):
            return JsonResponse(
                data={'message': 'Authorization has failed. Please send valid token.'},
                status=401
            )
