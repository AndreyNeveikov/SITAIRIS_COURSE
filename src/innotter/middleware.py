import jwt

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from user.models import User


class JWTAuthMiddleware(MiddlewareMixin):
    @staticmethod
    def check_if_access_token_exist(access_token):
        return access_token and access_token.startswith(settings.AUTH_HEADER_TYPE)

    def process_request(self, request):
        if request.get_full_path() not in settings.AUTH_URL_PATH:
            access_token = request.headers.get('Authorization', None)

            if self.check_if_access_token_exist(access_token):
                try:
                    payload = jwt.decode(
                        jwt=access_token.replace(settings.AUTH_HEADER_TYPE, ''),
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
            else:
                return JsonResponse(
                    data={'message': 'Authorization not found. Please send valid token in headers'},
                    status=401
                )

        return None


class BaseJWT:
    def __init__(self, user=None, token=None):
        self.user = user
        self.token = token

    def decode(self, key):
        payload = jwt.decode(jwt=self.token,
                             key=key,
                             algorithms=settings.JWT_ALGORITHM)
        return payload

    @property
    def get_access_token(self):
        return self._generate_jwt_token(
            token_lifetime=settings.ACCESS_TOKEN_LIFETIME,
            token_type='access',
            token_key=settings.ACCESS_TOKEN_KEY
        )

    @property
    def get_refresh_token(self):
        return self._generate_jwt_token(
            token_lifetime=settings.REFRESH_TOKEN_LIFETIME,
            token_type='refresh',
            token_key=settings.REFRESH_TOKEN_KEY
        )

    def _generate_jwt_token(self, token_lifetime, token_type, token_key):
        """
        Generate a token that stores the user identifier.
        """
        token = jwt.encode(payload={'token_type': token_type,
                                    'exp': token_lifetime,
                                    'user_uuid': str(self.user.uuid)},
                           key=token_key,
                           algorithm=settings.JWT_ALGORITHM)

        return token
