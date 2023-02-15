from rest_framework import status
from rest_framework import views
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from user.serializers import (RegistrationSerializer,
                              LoginSerializer,
                              RefreshTokenSerializer)


class AuthMixin:
    def post(self, request):
        serializer = self.serializer_class(data=request.data)  # noqa
        serializer.is_valid(raise_exception=True)
        response_data = serializer.save()
        return Response(response_data, status=status.HTTP_200_OK)


class RegistrationAPIView(views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class LoginAPIView(AuthMixin, views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer


class RefreshTokenAPIView(AuthMixin, views.APIView):
    permission_classes = (AllowAny,)
    serializer_class = RefreshTokenSerializer
