import jwt

from django.conf import settings
from rest_framework.generics import get_object_or_404

from core.exceptions import (TokenExpiredSignatureError,
                             InvalidTokenError,
                             NoTokenError)
from user.models import User


class BaseTokenService:
    KEY = None
    TOKEN_TYPE = None
    TOKEN_LIFETIME = None

    def __init__(self, validated_data=None, request=None):
        if validated_data:
            self.token = validated_data.get(self.TOKEN_TYPE, None)
        elif request:
            self.token = request.headers.get('Authorization', None)
        self.__payload = None

    def is_valid(self):
        if not (self.token and
                self.token.startswith(settings.AUTH_HEADER_PREFIX)):
            raise NoTokenError

        try:
            self.__payload = jwt.decode(
                jwt=self.token.replace(settings.AUTH_HEADER_PREFIX, ''),
                key=self.KEY,
                algorithms=settings.JWT_ALGORITHM
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredSignatureError()

        except (jwt.InvalidTokenError, jwt.DecodeError):
            raise InvalidTokenError()

    def get_user_from_payload(self):
        uuid = self.__payload.get('user_uuid')
        user = get_object_or_404(User, uuid=uuid)
        return user

    def generate_jwt_token_dict(self, user):
        return {
            'access': self._generate_access_token(user),
            'refresh': self._generate_refresh_token(user),
        }

    @staticmethod
    def _generate_access_token(user):
        access_payload = {
            'token_type': 'access',
            'exp': settings.ACCESS_TOKEN_LIFETIME,
            'user_uuid': str(user.uuid)
        }

        access_token = jwt.encode(payload=access_payload,
                                  key=settings.ACCESS_TOKEN_KEY,
                                  algorithm=settings.JWT_ALGORITHM)
        return access_token

    @staticmethod
    def _generate_refresh_token(user):
        refresh_payload = {
            'token_type': 'refresh',
            'exp': settings.REFRESH_TOKEN_LIFETIME,
            'user_uuid': str(user.uuid)
        }
        refresh_token = jwt.encode(payload=refresh_payload,
                                   key=settings.REFRESH_TOKEN_KEY,
                                   algorithm=settings.JWT_ALGORITHM)

        return refresh_token


class MiddlewareTokenService(BaseTokenService):
    KEY = settings.ACCESS_TOKEN_KEY

    def __init__(self, request):
        super().__init__(request=request)


class AccessTokenService(BaseTokenService):
    KEY = settings.ACCESS_TOKEN_KEY
    TOKEN_TYPE = 'access'
    TOKEN_LIFETIME = settings.ACCESS_TOKEN_LIFETIME

    def __init__(self, validated_data):
        super().__init__(validated_data=validated_data)


class RefreshTokenService(BaseTokenService):
    KEY = settings.REFRESH_TOKEN_KEY
    TOKEN_TYPE = 'refresh'
    TOKEN_LIFETIME = settings.REFRESH_TOKEN_LIFETIME

    def __init__(self, validated_data):
        super().__init__(validated_data=validated_data)
