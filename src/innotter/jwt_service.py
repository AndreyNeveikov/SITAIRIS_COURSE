import jwt
from rest_framework.generics import get_object_or_404

from core.exceptions import TokenExpiredSignatureError, InvalidTokenError, NoTokenError
from innotter.settings import (AUTH_HEADER_PREFIX, ACCESS_TOKEN_LIFETIME,
                               ACCESS_TOKEN_KEY, JWT_ALGORITHM,
                               REFRESH_TOKEN_KEY, REFRESH_TOKEN_LIFETIME)
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
        if not (self.token and self.token.startswith(AUTH_HEADER_PREFIX)):
            raise NoTokenError

        try:
            self.__payload = jwt.decode(
                jwt=self.token.replace(AUTH_HEADER_PREFIX, ''),
                key=self.KEY,
                algorithms=JWT_ALGORITHM
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
            'exp': ACCESS_TOKEN_LIFETIME,
            'user_uuid': str(user.uuid)
        }

        access_token = jwt.encode(payload=access_payload,
                                  key=ACCESS_TOKEN_KEY,
                                  algorithm=JWT_ALGORITHM)
        return access_token

    @staticmethod
    def _generate_refresh_token(user):
        refresh_payload = {
            'token_type': 'refresh',
            'exp': REFRESH_TOKEN_LIFETIME,
            'user_uuid': str(user.uuid)
        }
        refresh_token = jwt.encode(payload=refresh_payload,
                                   key=REFRESH_TOKEN_KEY,
                                   algorithm=JWT_ALGORITHM)

        return refresh_token


class MiddlewareTokenService(BaseTokenService):
    KEY = ACCESS_TOKEN_KEY

    def __init__(self, request):
        super().__init__(request=request)


class AccessTokenService(BaseTokenService):
    KEY = ACCESS_TOKEN_KEY
    TOKEN_TYPE = 'access'
    TOKEN_LIFETIME = ACCESS_TOKEN_LIFETIME

    def __init__(self, validated_data):
        super().__init__(validated_data=validated_data)


class RefreshTokenService(BaseTokenService):
    KEY = REFRESH_TOKEN_KEY
    TOKEN_TYPE = 'refresh'
    TOKEN_LIFETIME = REFRESH_TOKEN_LIFETIME

    def __init__(self, validated_data):
        super().__init__(validated_data=validated_data)
