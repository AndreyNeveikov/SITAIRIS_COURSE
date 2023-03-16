import jwt
from fastapi import HTTPException

import settings


class BaseTokenService:
    def __init__(self, request):
        self.token = request.headers.get('authorization', None)
        self.__payload = None

    def is_valid(self):
        if not (self.token and
                self.token.startswith(settings.AUTH_HEADER_PREFIX)):
            raise HTTPException(status_code=401, detail='Token is not valid')

        try:
            self.__payload = jwt.decode(
                jwt=self.token.replace(settings.AUTH_HEADER_PREFIX, ''),
                key=settings.ACCESS_TOKEN_KEY,
                algorithms=settings.JWT_ALGORITHM
            )
        except jwt.ExpiredSignatureError as e:
            raise HTTPException(status_code=401, detail=str(e))

        except (jwt.InvalidTokenError, jwt.DecodeError) as e:
            raise HTTPException(status_code=401, detail=str(e))

    def get_user_uuid_from_payload(self):
        uuid = self.__payload.get('user_uuid')
        return uuid
