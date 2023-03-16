from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from jwt_service import BaseTokenService


class MyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token_service = BaseTokenService(request)
        token_service.is_valid()
        user_uuid = token_service.get_user_uuid_from_payload()
        request.state.user_uuid = user_uuid
        response = await call_next(request)
        return response
