from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from user.models import User
from user.serializers import (RegistrationSerializer,
                              LoginSerializer,
                              RefreshTokenSerializer)


class RegistrationAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer


class LoginAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer

    def get_object(self):
        email = self.request.data.get('email')
        user = User.objects.filter(email=email).first()
        return user

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        request.user = user
        return super().post(request, *args, **kwargs)


class RefreshTokenAPIView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = RefreshTokenSerializer
