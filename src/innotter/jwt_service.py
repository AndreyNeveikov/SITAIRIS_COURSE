import jwt

from core.exceptions import TokenExpiredSignatureError, InvalidTokenError
from innotter import settings
from user.models import User


def validate_token(token: str):
    return token and token.startswith(settings.AUTH_HEADER_PREFIX)


def generate_jwt_token_dict(user):
    return {
        'access': _generate_access_token(user),
        'refresh': _generate_refresh_token(user),
    }


def _generate_access_token(user: User):
    access_payload = {
        'token_type': 'access',
        'exp': settings.ACCESS_TOKEN_LIFETIME,
        'user_uuid': str(user.uuid)
    }

    access_token = jwt.encode(payload=access_payload,
                              key=settings.ACCESS_TOKEN_KEY,
                              algorithm=settings.JWT_ALGORITHM)
    return access_token


def _generate_refresh_token(user: User):
    refresh_payload = {
        'token_type': 'refresh',
        'exp': settings.REFRESH_TOKEN_LIFETIME,
        'user_uuid': str(user.uuid)
    }
    refresh_token = jwt.encode(payload=refresh_payload,
                               key=settings.REFRESH_TOKEN_KEY,
                               algorithm=settings.JWT_ALGORITHM)

    return refresh_token


def decode_access_token(access_token):
    return _decode_token(access_token, settings.ACCESS_TOKEN_KEY)


def decode_refresh_token(refresh_token):
    return _decode_token(refresh_token, settings.REFRESH_TOKEN_KEY)


def _decode_token(token, token_key):
    try:
        payload = jwt.decode(
            jwt=token.replace(settings.AUTH_HEADER_PREFIX, ''),
            key=token_key,
            algorithms=settings.JWT_ALGORITHM
        )
    except jwt.ExpiredSignatureError:
        raise TokenExpiredSignatureError()

    except (jwt.InvalidTokenError, jwt.DecodeError):
        raise InvalidTokenError()

    return payload
