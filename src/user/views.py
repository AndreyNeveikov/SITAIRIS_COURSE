from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from user.models import User
from user.permissions import IsAdmin, IsOwner
from user.serializers import (RegistrationSerializer,
                              LoginSerializer,
                              RefreshTokenSerializer,
                              UserSerializer)
from user.services import AdminService


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    permission_action_classes = {
        'register': [AllowAny],
        'login': [AllowAny],
        'refresh': [AllowAny],
        'update': [IsAuthenticated, IsOwner],
        'partial_update': [IsAuthenticated, IsOwner],
        'block_user': [IsAuthenticated, IsAdmin]
    }
    serializer_action_classes = {
        'login': LoginSerializer,
        'register': RegistrationSerializer,
        'refresh': RefreshTokenSerializer,
    }

    def get_serializer_class(self):
        return self.serializer_action_classes.get(self.action, UserSerializer)

    def get_permissions(self):
        permissions = self.permission_action_classes.get(
            self.action, [IsAuthenticated]
        )
        return [permission() for permission in permissions]

    @action(detail=False, methods=['post'])
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def refresh(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def block_user(self, request, user_id):
        admin_service = AdminService(user_id)
        admin_service.toggle_block_status()
        response = admin_service.get_block_status_response()
        return Response(data=response,
                        status=status.HTTP_200_OK)
