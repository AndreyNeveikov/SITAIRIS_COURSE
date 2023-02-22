from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


class InvalidTokenError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _(
        'Authorization has failed. Please send valid token.'
    )
    default_code = 'authentication_failed'


class TokenExpiredSignatureError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = _('Authentication token has expired')
    default_code = 'authentication_failed'


class NoTokenError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _(
        'Authorization not found. Please send valid token in headers'
    )
    default_code = 'authentication_failed'

