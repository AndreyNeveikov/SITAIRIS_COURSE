import jwt

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.deprecation import MiddlewareMixin

from user.models import User


class JWTAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # If user want to log in or register
        if request.path in settings.AUTH_URL_PATH:
            return None

        # Get token from headers
        access_token = request.headers.get('Authorization', None)

        if access_token:
            try:
                keyword, token_id = access_token.split()
            except ValueError:
                return JsonResponse(
                    data={'message': 'Authorization not found. Please send valid token in headers'},
                    status=401
                )
            else:
                if keyword not in settings.AUTH_HEADER_TYPES:
                    return JsonResponse(
                        data={'message': 'Authorization not found. Please send valid token in headers'},
                        status=401
                    )

            #
            if request.path in settings.REFRESH_TOKEN_PATH:
                key = settings.REFRESH_TOKEN_KEY
            else:
                key = settings.ACCESS_TOKEN_KEY


            auth = BaseJWT(token=token_id)

            # Get payload
            try:
                payload = auth.decode(key=key)
            except jwt.ExpiredSignatureError:
                return JsonResponse({'message': 'token expired error'}, status=401)
            except (jwt.InvalidTokenError, jwt.DecodeError):
                return JsonResponse({'message': 'token invalid error'}, status=401)
            else:
                user_uuid = payload.get('user_uuid')
                request.user = get_object_or_404(User, uuid=user_uuid)
                return None
        else:
            return JsonResponse(
                data={'message': 'Authorization not found. Please send valid token in headers'},
                status=401
            )


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


# class JWTAuthMiddleware(MiddlewareMixin):
#     def process_request(self, request):  # noqa
#
#         # If user want to log in or register
#         if request.path in settings.AUTH_URL_PATH:
#             return None
#
#         # Get token from headers
#         access_token = request.headers.get('Authorization', None)
#
#         # Validate token
#         try:
#             keyword, token_id = access_token.split()
#             if keyword not in settings.AUTH_HEADER_TYPES:
#                 return JsonResponse(
#                     data={'message': 'Authorization not found. Please send valid token in headers'},
#                     status=401
#                 )
#
#         except (ValueError, AttributeError):
#             return JsonResponse(
#                 data={'message': 'Authorization not found. Please send valid token in headers'},
#                 status=401
#             )
#
#         # Get payload
#         try:
#             payload = jwt.decode(jwt=token_id,
#                                  key=settings.SECRET_KEY,
#                                  algorithms=settings.JWT_ALGORITHM)
#         except jwt.ExpiredSignatureError:
#             return JsonResponse({'message': 'token expired error'}, status=401)
#         except (jwt.InvalidTokenError, jwt.DecodeError):
#             return JsonResponse({'message': 'token invalid error'}, status=401)
#         else:
#             user_uuid = payload.get('user_uuid')
#             request.user = get_object_or_404(User, uuid=user_uuid)
#             return None
