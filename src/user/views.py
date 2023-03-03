from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from core.permissions import IsAdmin, IsModerator
from core.serializers import ImageSerializer
from user.models import User
from user.permissions import IsOwner
from user.serializers import (LoginSerializer,
                              RefreshTokenSerializer,
                              UserSerializer, UserUpdateSerializer,
                              UserCreateSerializer)
from user.services import AdminService


class UserViewSet(mixins.RetrieveModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    permission_action_classes = {
        'register': [AllowAny],
        'login': [AllowAny],
        'refresh': [AllowAny],
        'update': [IsAuthenticated, IsOwner],
        'partial_update': [IsAuthenticated, IsOwner],
        'block_user': [IsAuthenticated, IsAdmin],
        'list': [IsAuthenticated, IsAdmin | IsModerator]
    }
    serializer_action_classes = {
        'login': LoginSerializer,
        'refresh': RefreshTokenSerializer,
        'create': UserCreateSerializer,
        'update': UserUpdateSerializer,
        'partial_update': UserUpdateSerializer
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

    @action(detail=True, methods=['post'])
    def block_user(self, request, pk):
        admin_service = AdminService(pk)
        admin_service.toggle_block_status()
        response = admin_service.get_block_status_response()
        return Response(data=response,
                        status=status.HTTP_200_OK)
